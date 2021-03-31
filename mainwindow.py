import sys

from PySide6.QtCore import (Qt, QSettings)
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidget,
                               QTableWidgetItem, QSizePolicy, QMessageBox,
                               QDialog, QHBoxLayout, QTreeWidgetItem,
                               QVBoxLayout)

from gui import ui_mainwindow
from gui.ui_functions import *

from section import Section
from plate import Plate
from service import StandardDataService, OrderDataService
from page import OrderPage
from dialogs import NewOrderDialog, CloseOrderDialog
from catalog import Catalog
from settings import Settings


class MainWindow (QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = ui_mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)

        # Установка визуальных дополнений приложения
        UIFunctions.set_application_styles(self)
        UIFunctions.set_topbar_shadow(self)

        # Текущий заказ, информация о котором отображается в главном окне
        self.current_order = OrderContext()
        self.current_section = None

        # Работа с настройками приложения: подгрузка настроек
        self.settings = QSettings('configs', QSettings.IniFormat, self)
        self.is_saved = True

        self.cut_allowance = None          # Припуск на разрез
        self.end_face_loss = None          # Потери при обработке торцов (%)
        self.minimum_plate_width = None    # Минимальная ширина пластины
        self.minimum_plate_height = None   # Минимальная длина пластины
        self.rough_roll_edge_loss = None   # Потери при обработке кромки до 3мм
        self.clean_roll_edge_loss = None   # Потери при обработке кромки на 3мм

        self.guillotine_width = 1200       # Ширина ножа гильотины
        self.maximum_plate_height = 1200   # Максимальная длина пластины
        self.rough_roll_plate_width = 400  # Ширина пластины проката до 3мм
        self.clean_roll_plate_width = 450  # Ширина пластины проката на 3мм
        self.clean_roll_depth = 3          # Толщина чистового проката
        self.admissible_deformation = 70   # Допустимая деформация проката (%)

        self.readSettings()

        # Заполняем список заказов из базы
        self.loadOrderList()

        # Соединяем сигналы окна со слотами класса
        self.ui.newOrder.clicked.connect(self.open_new_order)
        self.ui.catalog.clicked.connect(self.open_catalog)
        self.ui.settings.clicked.connect(self.open_settings)
        self.ui.closeOrder.clicked.connect(self.open_close_order)
        self.ui.information.clicked.connect(
            lambda: (
                self.ui.mainArea.setCurrentIndex(0),
                self.ui.information.setChecked(True)
            )
        )

    def loadOrderList(self):

        order_list = OrderDataService.get_table('orders')
        layout = QVBoxLayout()
        layout.setSpacing(10)

        for order in order_list:
            order_section = Section(order[0], order[1])
            order_section.setContentFields(
                self.createOrderTable(order[0], *order[2:])
            )
            order_section.clicked.connect(self.showOrderInformation)
            layout.addWidget(order_section)

        layout.setContentsMargins(0, 0, 7, 0)
        layout.addStretch()
        self.ui.scrollAreaWidgetContents.setLayout(layout)

    def loadDetailList(self, depth: float = 0):

        cut_blanks = OrderDataService.cut_blanks(
            {'order_id': self.current_order.getID()}, depth)
        layout = QVBoxLayout()
        layout.setSpacing(10)

        for detail in cut_blanks:
            detail_section = Section(detail[0], detail[1])
            detail_section.setContentFields(
                self.createDetailTable(*detail[2:])
            )
            layout.addWidget(detail_section)

        layout.setContentsMargins(0, 0, 7, 0)
        layout.addStretch()
        self.ui.scrollAreaWidgetContents_2.setLayout(layout)

    def createOrderTable(self, id: int, amount: int, status: str,
                         depth: float = 1.0,
                         efficiency: float = 100.0) -> QVBoxLayout:

        data = {
            'Состав заказа': str(amount) + ' изд.',
            'Статус заказа': status.capitalize()
        }
        if efficiency:
            data['Выход годного'] = str(efficiency) + '%'
        if depth:
            data['Текущая толщина'] = str(depth) + ' мм'

        table = QTableWidget(len(data), 2)

        table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.horizontalHeader().hide()
        table.verticalHeader().hide()
        table.horizontalHeader().setStretchLastSection(True)

        for row, values in enumerate(data.items()):
            table.setItem(row, 0, QTableWidgetItem(values[0]))
            table.setItem(row, 1, QTableWidgetItem(values[1]))

        table.resizeColumnToContents(0)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(table)
        return layout

    def createDetailTable(self, fusion: str, amount: int, height: int,
                          width: int, depth: float) -> QVBoxLayout:

        data = {
            'Сплав': fusion,
            'Количество': str(amount) + ' шт.',
            'Размеры': f'{height}x{width}x{depth}'
        }

        table = QTableWidget(3, 2)

        table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.horizontalHeader().hide()
        table.verticalHeader().hide()
        table.horizontalHeader().setStretchLastSection(True)

        for row, values in enumerate(data.items()):
            table.setItem(row, 0, QTableWidgetItem(values[0]))
            table.setItem(row, 1, QTableWidgetItem(values[1]))

        table.resizeColumnToContents(0)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(table)
        return layout

    def showOrderInformation(self):

        choosen_order = self.sender()

        if not self.current_section:
            self.current_section = choosen_order
        elif choosen_order is self.current_section:
            self.current_section = None
            self.ui.orderInformationArea.setCurrentWidget(self.ui.defaultPage)
            return
        else:
            self.current_section.collapse()
            self.current_section = choosen_order
        page = self.createInformationPage()
        self.setInformationPage(page)

    def createInformationPage(self):

        page = OrderPage()

        id = self.current_section.getID()
        data = OrderDataService.get_by_id('orders', {'order_id': id})
        status, name, depth, efficiency, on_storage = data[1:]
        ingots = OrderDataService.ingots({'order_id': id})
        complects = OrderDataService.complects({'order_id': id})

        # Если статус "в работе", то скрыть статистику и остатки
        if status == 1 or status == 2:
            page.ui.label_4.hide()
            page.ui.label_5.hide()
            page.ui.label_6.hide()
            page.ui.scrollArea_3.hide()
        # Если статус "не начат", то скрыть статистику, карту и остатки
        # TODO: НА ДАННЫЙ МОМЕНТ НЕ РАБОТАЕТ - НЕТ НЕ НАЧАТЫХ ЗАКАЗОВ
        elif status == 3:
            page.ui.label_4.hide()
            page.ui.label_5.hide()
            page.ui.label_6.hide()
            page.ui.label_7.hide()
            page.ui.scrollArea_3.hide()
            page.ui.graphicsView.hide()
        # Если статус "завершён", то скрыть кнопку перехода к подробному плану
        elif status == 4 or status == 5:
            page.ui.detailedPlanFrame.hide()

        # Назначение названия заказа
        storage = ' (на склад)' if int(on_storage) else ''
        page.ui.label.setText('Заказ ' + name + storage)

        # Назначение списка изделий и деталей заказа
        for article, details in complects.items():
            article_item = QTreeWidgetItem(
                page.ui.treeWidget, [article[1], None, None])

            for detail in details:
                detail_item = QTreeWidgetItem(
                    article_item, [detail[1], str(detail[2]), str(detail[3])])

            page.ui.treeWidget.addTopLevelItem(article_item)
        page.ui.treeWidget.resizeColumnToContents(0)

        # Назначение слитков заказа
        ingots_layout = QHBoxLayout()
        for ingot in ingots:
            ingot_plate = Plate(ingot[0], ingot[1], ingot[2], ingot[3:])
            ingots_layout.addWidget(ingot_plate)
        ingots_layout.setContentsMargins(0, 0, 0, 0)
        ingots_layout.setSpacing(0)
        ingots_layout.addStretch()
        page.ui.scrollAreaWidgetContents_3.setLayout(ingots_layout)

        self.current_order.id = self.current_section.id
        self.current_order.ingots = ingots
        self.current_order.complects = complects

        page.ui.detailedPlan.clicked.connect(
            lambda: (
                self.ui.mainArea.setCurrentIndex(1),
                self.ui.chart.setChecked(True),
                self.createDepthLineBar()
                self.loadDetailList()
            )
        )

        return page

    def setInformationPage(self, page: OrderPage):

        self.ui.informationPage.layout().takeAt(0)
        self.ui.informationPage.layout().addWidget(page)
        self.ui.orderInformationArea.setCurrentWidget(self.ui.informationPage)

    def open_catalog(self):
        window = Catalog(self)
        window.show()

    def open_settings(self):
        window = Settings(self, self.settings)
        if window.exec_() == QDialog.Accepted:
            self.readSettings()

    def open_new_order(self):
        window = NewOrderDialog(self)
        window.exec_()

    def open_close_order(self):
        window = CloseOrderDialog(self)
        window.exec_()

    def readSettings(self):

        self.cut_allowance = self.settings.value(
            'cutting/cut_allowance', defaultValue=2, type=int)
        self.end_face_loss = self.settings.value(
            'cutting/end_face', defaultValue=0.01, type=float)
        self.minimum_plate_width = self.settings.value(
            'cutting/min_width', defaultValue=50, type=int)
        self.guillotine_width = self.settings.value(
            'cutting/guilliotine', defaultValue=1200, type=int)
        self.minimum_plate_height = self.settings.value(
            'cutting/min_height', defaultValue=100, type=int)
        self.maximum_plate_height = self.settings.value(
            'cutting/max_height', defaultValue=1200, type=int)

        self.clean_roll_depth = self.settings.value(
            'rolling/clean_depth', defaultValue=3, type=int)
        self.rough_roll_edge_loss = self.settings.value(
            'rolling/rough_edge', defaultValue=4, type=int)
        self.clean_roll_edge_loss = self.settings.value(
            'rolling/clean_edge', defaultValue=2, type=int)
        self.admissible_deformation = self.settings.value(
            'rolling/deformation', defaultValue=0.7, type=float)
        self.rough_roll_plate_width = self.settings.value(
            'rolling/max_rough_width', defaultValue=450, type=int)
        self.clean_roll_plate_width = self.settings.value(
            'rolling/max_clean_width', defaultValue=400, type=int)

    def writeSettings(self):

        self.settings.setValue(
            'cutting/end_face', self.end_face_loss)
        self.settings.setValue(
            'cutting/cut_allowance', self.cut_allowance)
        self.settings.setValue(
            'cutting/guilliotine', self.guillotine_width)
        self.settings.setValue(
            'cutting/min_width', self.minimum_plate_width)
        self.settings.setValue(
            'cutting/min_height', self.minimum_plate_height)
        self.settings.setValue(
            'cutting/max_height', self.maximum_plate_height)

        self.settings.setValue(
            'rolling/clean_depth', self.clean_roll_depth)
        self.settings.setValue(
            'rolling/rough_edge', self.rough_roll_edge_loss)
        self.settings.setValue(
            'rolling/clean_edge', self.clean_roll_edge_loss)
        self.settings.setValue(
            'rolling/deformation', self.admissible_deformation)
        self.settings.setValue(
            'rolling/max_rough_width', self.rough_roll_plate_width)
        self.settings.setValue(
            'rolling/max_clean_width', self.clean_roll_plate_width)

    def closeEvent(self, event):
        event.accept()

        # TODO: разобрать эту помойку на запчасти, а может и вовсе удалить
        # want_to_exit = QMessageBox.question(
        #     self,
        #     'Выход',
        #     'Вы уверены, что хотите выйти?',
        #     QMessageBox.Ok | QMessageBox.Cancel
        # )
        # if want_to_exit == QMessageBox.Ok:
        #     self.writeSettings()
        #     event.accept()
        # else:
        #     event.ignore()


class OrderContext:

    def __init__(self):
        self.order_id = 0
        self.order_ingots = []
        # TODO: как оформить дерево - не знаю, но число деревьев зависит от
        #       числа слитков, которые указаны в заказе
        self.cutting_trees = {}
        self.order_complects = []
        self.current_depth = 0.0
        self.order_efficiency = 0


    @property
    def id(self):
        return self.order_id

    @id.setter
    def id(self, value: int):
        self.order_id = value

    @property
    def ingots(self):
        return self.order_ingots

    @ingots.setter
    def ingots(self, value: []):
        self.order_ingots = value
        self.cutting_trees = dict.fromkeys()

    @property
    def complects(self):
        return self.order_complects

    @complects.setter
    def complects(self, value: []):
        self.order_complects = value

    @property
    def depth(self):
        return self.current_depth

    @depth.setter
    def depth(self, value: float):
        self.current_depth = value

    @property
    def efficiency(self):
        return self.order_efficiency


if __name__ == '__main__':
    application = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(application.exec_())
