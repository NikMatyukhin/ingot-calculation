import sys
from typing import Iterable, Union
from itertools import chain
from operator import itemgetter, attrgetter

from PySide6.QtCore import (Qt, QSettings)
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidget,
                               QTableWidgetItem, QSizePolicy, QMessageBox,
                               QDialog, QHBoxLayout, QTreeWidgetItem,
                               QVBoxLayout, QPushButton)

from gui import ui_mainwindow
from gui.ui_functions import *

from sequential_mh.bpp_dsc.rectangle import (
    Direction, Material, Blank, Kit, Bin
)
from sequential_mh.bpp_dsc.tree import (
    BinNode, Tree, optimal_configuration, solution_efficiency,
    CuttingChartNode
)
from sequential_mh.bpp_dsc.stm import _stmh_idrd

from section import Section
from plate import Plate
from service import StandardDataService, OrderDataService
from page import OrderPage
from dialogs import NewOrderDialog, CloseOrderDialog
from catalog import Catalog
from settings import Settings


Number = Union[int, float]
Sizes = tuple[Number, Number, Number]
ListSizes = list[Sizes]


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
        self.ui.pushButton_1.clicked.connect(self.depthLineChanged)

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

        len = self.ui.verticalLayout_8.count()
        for _ in range(len-1):
            item = self.ui.verticalLayout_8.takeAt(0)
            item.widget().hide()
            self.ui.verticalLayout_8.removeWidget(item.widget())

        cut_blanks = OrderDataService.cut_blanks(
            {'order_id': self.current_order.id}, depth)

        for detail in cut_blanks:
            detail_section = Section(detail[0], detail[1])
            detail_section.setContentFields(
                self.createDetailTable(*detail[2:])
            )
            self.ui.verticalLayout_8.insertWidget(0, detail_section)

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

        id = self.current_section.id
        data = OrderDataService.get_by_id('orders', {'order_id': id})
        status, name, depth, efficiency, on_storage = data[1:]
        ingots = OrderDataService.ingots({'order_id': id})
        complects = OrderDataService.complects({'order_id': id})

        # пока работаем только с одном слитком
        main_ingot = ingots[0][-3:]

        # TODO: Вторым аргументом нужно вставить плотность сплава
        material = Material(main_ingot[1], 2.2, 1.)

        # выбор заготовок и удаление лишних значений
        details_info = map(
            itemgetter(0), chain.from_iterable(complects.values())
        )
        details = self.getDetails(details_info, material)

        self.createCut(main_ingot, details, material)

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
                self.createDepthLineBar(),
                self.loadDetailList()
            )
        )

        return page

    def setInformationPage(self, page: OrderPage):

        self.ui.informationPage.layout().takeAt(0)
        self.ui.informationPage.layout().addWidget(page)
        self.ui.orderInformationArea.setCurrentWidget(self.ui.informationPage)

    def createDepthLineBar(self):
        len = self.ui.horizontalLayout_6.count()
        for _ in range(len-1):
            self.ui.horizontalLayout_6.takeAt(1)
        leaves: list[CuttingChartNode] = self.current_order.tree.cc_leaves
        leaves.sort(key=attrgetter('bin.height'), reverse=True)
        for leave in leaves:
            depth = leave.bin.height
            button = QPushButton(f'{depth} мм')
            button.setCheckable(True)
            button.setAutoExclusive(True)
            button.setStyleSheet('''
                QPushButton {
                    border: none;
                    background-color: rgb(225, 225, 225);
                    width: 80px;
                    height: 40px;
                    padding: 0px;
                    color: black;
                }

                QPushButton:hover {
                    background-color: rgb(235, 235, 235);
                    border-bottom: 3px solid gray;
                    font-weight: 800;
                    padding-top: 3px;
                }

                QPushButton:pressed {
                    background-color: rgb(245, 245, 245);
                    border-bottom: 3px solid gray;
                    font-weight: 800;
                    padding-top: 3px;
                }

                QPushButton:checked {
                    background-color: rgb(225, 225, 225);
                    border-bottom: 3px solid black;
                    padding-top: 3px;
                    font-weight: 800;
                }''')
            button.clicked.connect(self.depthLineChanged)
            self.ui.horizontalLayout_6.addWidget(button)
        self.ui.horizontalLayout_6.addStretch()

    def depthLineChanged(self):
        button = self.sender()
        name = button.text()
        if name.startswith('Исходная'):
            self.loadDetailList()
        else:
            depth, _, _ = name.partition(' ')
            self.loadDetailList(depth=float(depth))

    def getDetails(self, details_id: Iterable[int], material: Material) -> Kit:
        """Формирование набора заготовок

        :param details_id: Список id заготовок
        :type details_id: Iterable[int]
        :param material: Материал
        :type material: Material
        :return: Набор заготовок
        :rtype: Kit
        """
        # выбор заготовок и удаление лишних значений
        details = []
        for id_ in details_id:
            detail = StandardDataService.get_by_id(
                'details', {'detail_id': id_}
            )
            amount = detail[-3]
            size: Sizes = detail[4:-3]
            # если в Базе не будет нулевых размеров, можно убрать
            if 0 in size:
                continue
            priority: int = detail[-2]
            direction: int = detail[-1]
            for _ in range(amount):
                blank = Blank(
                    *size, priority, direction=Direction(direction),
                    material=material
                )
                details.append(blank)
        kit = Kit(details)
        kit.sort('width')
        return kit

    def createCut(self, ingot_size: Sizes, kit: Kit, material: Material):
        """Метод запуска алоритма раскроя

        :param ingot_size: Размер слитка в формате (длина, ширина, толщина)
        :type ingot_size: tuple[Number, Number, Number]
        :param kit: Набор заготовок
        :type kit: Kit
        :param material: Материал
        :type material: Material
        """
        # считать настройки и сложить в словарь
        self.readSettings()
        settings = {
            'max_size': (
                (self.maximum_plate_height, self.clean_roll_plate_width),
                (self.maximum_plate_height, self.rough_roll_plate_width)
                # (2000, self.clean_roll_plate_width),
                # (2000, self.rough_roll_plate_width)
            ),
            'cutting_length': self.guillotine_width,
            'cutting_thickness': 4.2,
            'hem_until_3': self.rough_roll_edge_loss,
            'hem_after_3': self.clean_roll_edge_loss,
            'allowance': self.cut_allowance,
            'end': self.end_face_loss,
        }
        bin_ = Bin(*ingot_size, material=material)
        root = BinNode(bin_, kit=kit)
        tree = Tree(root)
        tree = _stmh_idrd(tree, restrictions=settings)
        _, self.current_order.tree, _ = optimal_configuration(tree, nd=True)

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
        self.root = None
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
    def tree(self):
        return self.root

    @tree.setter
    def tree(self, value: BinNode):
        self.root = value
        self.root.update_size()

    @property
    def efficiency(self):
        return self.order_efficiency


if __name__ == '__main__':
    application = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(application.exec_())
