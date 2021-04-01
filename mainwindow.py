import sys
from typing import Iterable, Union, NoReturn
from itertools import chain
from operator import itemgetter, attrgetter

from PySide6.QtCore import (
    Qt, QSettings, Signal
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QTreeWidgetItem,
    QMessageBox, QDialog, QHBoxLayout, QSizePolicy, QVBoxLayout, QPushButton,
    QLayout, QGraphicsScene
)

from gui import ui_mainwindow
from gui.ui_functions import *

from plate import Plate
from page import OrderPage
from section import Section
from button import ExclusiveButton
from charts.plan import CuttingPlanPainter

from sequential_mh.bpp_dsc.rectangle import (
    Direction, Material, Blank, Kit, Bin
)
from sequential_mh.bpp_dsc.tree import (
    BinNode, Tree, optimal_configuration, solution_efficiency,
    CuttingChartNode
)
from sequential_mh.bpp_dsc.stm import _stmh_idrd

from service import StandardDataService, OrderDataService
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
        self.cutting_thickness = 4.2       # Толщина начала разрезов

        self.readSettings()

        # Сцены для отрисовки
        self.plan_scene = QGraphicsScene()
        self.ui.graphicsView.setScene(self.plan_scene)
        self.ui.graphicsView.scale(1.9, 1.9)
        self.ui.graphicsView.setAlignment(Qt.AlignCenter)
        self.plan_painter = CuttingPlanPainter(self.plan_scene)

        # Заполняем список заказов из базы
        self.loadOrderList()

        # Соединяем сигналы окна со слотами класса
        self.ui.newOrder.clicked.connect(self.openNewOrder)
        self.ui.catalog.clicked.connect(self.openCatalog)
        self.ui.settings.clicked.connect(self.openSettings)

        # Сигнал перехода на следующий шаг заказа
        self.ui.closeOrder.clicked.connect(self.openCloseOrder)

        # Сигнал возврата на исходную страницу с информацией о заказах
        self.ui.information.clicked.connect(
            lambda: (
                self.ui.mainArea.setCurrentIndex(0),
                self.ui.information.setChecked(True),
                self.plan_painter.clearCanvas()
            )
        )

        # Кнопку "Исходная пластина" привызяваем отдельно от всех
        self.ui.sourcePlate.clicked.connect(self.depthLineChanged)

    def loadOrderList(self) -> NoReturn:
        """Подгрузка списка заказов

        Загружается список заказов из таблицы заказов и на его основе
        формируется скомпанованный слой из виджетов Section с информацией.
        TODO: Список заказов создаётся один раз и не меняется впоследствии.
              стоит доработать по типу списка заготовок, но не сейчас.
        """
        order_list = OrderDataService.get_table('orders')
        layout = QVBoxLayout()
        layout.setSpacing(10)
        for order in order_list:
            order_section = Section(order[0], order[1])
            order_section.setContentFields(
                self.createOrderTable(order[0], *order[2:])
            )
            order_section.st_name = order[3]
            order_section.depth = order[4]
            order_section.efficiency = order[5]
            order_section.clicked.connect(self.showOrderInformation)
            layout.addWidget(order_section)
        layout.setContentsMargins(0, 0, 7, 0)
        layout.addStretch()
        self.ui.scrollAreaWidgetContents.setLayout(layout)

    def createOrderTable(self, id: int, amount: int, status: str,
                         depth: float, efficiency: float) -> QVBoxLayout:
        """Создание информационной таблички заказа

        Принимая основные характеристики заполняемого заказа формируется
        табличка QTableWidget и устанавливается на возвращаемый слой.

        :param id: Идентификатор записи заказа - забыл, зачем добавил
        :type id: int
        :param amount: Количество изделий в заказе - первая строка
        :type amount: int
        :param status: Статус заказа текстом - вторая строка
        :type status: str
        :param depth: Текущая толщина в заказе - третья строка
        :type depth: float
        :param efficiency: Выход годного в заказе - третья или четвёртая строка
        :type efficiency: float
        :return: Скомпанованный слой с таблицей внутри
        :rtype: QVBoxLayout
        """
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

    def showOrderInformation(self) -> NoReturn:
        """Переключатель активных заказов и открытых секций

        Отвечает за то, чтобы одновременно была раскрыта только одна секция
        из списка заказов. Подгружает новую страницу заказа при его выборе.
        TODO: Вместо постоянного пересоздавания страницы заказа нужно создать
              его в формочке и просто заполнять нужные данные.
        """
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
        self.ui.informationPage.layout().takeAt(0)
        self.ui.informationPage.layout().addWidget(page)
        self.ui.orderInformationArea.setCurrentWidget(self.ui.informationPage)

    def createInformationPage(self) -> NoReturn:
        """Создание страницы информации о заказе

        Собирает все данные о текущем заказе и выгружает их на страницу.
        TODO: Встроить её в начальное окно и там настроить работу этого окна.
        """
        page = OrderPage()

        id = self.current_section.id
        data = OrderDataService.get_by_id('orders', {'order_id': id})
        status, name, depth, efficiency, on_storage = data[1:]
        ingots = OrderDataService.ingots({'order_id': id})
        complects = OrderDataService.complects({'order_id': id})

        # Пока работаем только с одном слитком
        main_ingot = ingots[0][-3:]

        # TODO: Вторым аргументом нужно вставить плотность сплава
        material = Material(main_ingot[1], 2.2, 1.)

        # Выбор заготовок и удаление лишних значений
        details_info = map(
            itemgetter(0), chain.from_iterable(complects.values())
        )
        details = self.getDetails(details_info, material)

        self.createCut(main_ingot, details, material)

        page.hideForStatus(status)
        page.setPageTitle(name, on_storage)
        page.setComplects(complects)
        page.setIngots(ingots)
        page.ui.detailedPlan.clicked.connect(
            lambda: (
                self.ui.mainArea.setCurrentIndex(1),
                self.ui.chart.setChecked(True),
                self.chartPagePreparation()
            )
        )
        page.drawCuttingMap(self.current_order.tree)

        # Заполнение данных сущности текущего заказа
        self.current_order.id = self.current_section.id
        self.current_order.name = self.current_section.name
        self.current_order.st_name = self.current_section.st_name
        self.current_order.efficiency = self.current_section.efficiency
        self.current_order.depth = self.current_section.depth
        self.current_order.ingots = ingots
        self.current_order.complects = complects

        return page

    def getDetails(self, details_id: Iterable[int], material: Material) -> Kit:
        """Формирование набора заготовок

        :param details_id: Список id заготовок
        :type details_id: Iterable[int]
        :param material: Материал
        :type material: Material
        :return: Набор заготовок
        :rtype: Kit
        """
        details = []
        for id_ in details_id:
            detail = OrderDataService.get_detail(
                {'order_id': self.current_section.id},
                {'detail_id': id_}
            )
            amount = detail[0]
            size: Sizes = detail[1:4]
            # если в Базе не будет нулевых размеров, можно убрать
            if 0 in size:
                continue
            priority: int = detail[4]
            direction: int = detail[5]
            for _ in range(amount):
                blank = Blank(
                    *size, priority, direction=Direction(direction),
                    material=material
                )
                blank.name = detail[6]
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

    def chartPagePreparation(self) -> NoReturn:
        """Подготовка страницы с планами раскроя

        Подгрузка списка заготовок, формирование кнопок толщин.
        """
        self.clearLayout(self.ui.horizontalLayout_6, take=1)

        for depth in self.current_order.depth_list:
            button = ExclusiveButton(depth=depth)
            button.clicked.connect(self.depthLineChanged)
            self.ui.horizontalLayout_6.addWidget(button)
        self.ui.horizontalLayout_6.addStretch()
        self.ui.sourcePlate.setChecked(True)

        self.sourcePage()

        # Кнопку заверешния заказа меняем на кнопку перехода на след.шаг
        depth = self.current_order.depth
        self.ui.closeOrder.setText('Завершить ' + str(depth) + ' мм')

    def depthLineChanged(self) -> NoReturn:
        """Просмотр другой толщины и подгрузка нового списка деталей"""
        button = self.sender()
        self.plan_painter.clearCanvas()
        if button is self.ui.sourcePlate:
            self.sourcePage()
        else:
            depth = button.depth
            self.stepPage(depth)

    def sourcePage(self):
        self.loadDetailList(depth=0.0)
        bin = self.current_order.root.bin
        self.plan_painter.setBin(
            round(bin.length, 1),
            round(bin.width, 1),
            round(bin.height, 1)
        )
        self.plan_painter.drawBin()

    def stepPage(self, depth: float):
        self.loadDetailList(depth=float(depth))
        index = self.current_order.depth_index(depth)
        pack = self.current_order.root.cc_leaves[index]
        self.plan_painter.setBin(
            round(pack.bin.length, 1),
            round(pack.bin.width, 1),
            round(pack.bin.height, 1)
        )
        for blank in pack.result:
            rect = blank.rectangle
            self.plan_painter.addBlank(
                round(rect.length, 1),
                round(rect.width, 1),
                round(rect.height, 1),
                round(blank.x, 1),
                round(blank.y, 1),
                rect.name
            )
        self.plan_painter.drawPlan()

    def loadDetailList(self, depth: float) -> NoReturn:
        """Подгрузка списка заготовок

        Список заготовок конкретной толщины, если выбрана толщина, но
        полный список всех заготовок заказа, если выбрана <Исходная пластина>.
        """
        self.clearLayout(self.ui.verticalLayout_8, hidden=True)
        id = self.current_order.id
        cut_blanks = OrderDataService.cut_blanks({'order_id': id}, depth)
        for detail in cut_blanks:
            detail_section = Section(detail[0], detail[1])
            detail_section.setContentFields(
                self.createDetailTable(*detail[2:])
            )
            self.ui.verticalLayout_8.insertWidget(0, detail_section)

    def createDetailTable(self, fusion: str, amount: int, height: int,
                          width: int, depth: float) -> QVBoxLayout:
        """Создание информационной таблички заготовки

        Принимая основные характеристики заполняемой заготовки формируется
        табличка QTableWidget и устанавливается на возвращаемый слой.

        :param fusion: Сплав из которого выполняется заготовка - первая строка
        :type fusion: str
        :param amount: Количество заготовок в заказе - вторая строка
        :type amount: int
        :param height: Длина заготовки - третья строка
        :type heithg: int
        :param width: Ширина заготовки - третья строка
        :type width: int
        :param depth: Толщина заготовки - третья строка
        :type depth: float
        :return: Скомпанованный слой с таблицей внутри
        :rtype: QVBoxLayout
        """
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

    def clearLayout(self, layout: QLayout, take: int = 0,
                    hidden: bool = False) -> NoReturn:
        """Метод для очистки слоёв компановки

        :param layout: Слой с которого удаляются виджеты по заданным правилам
        :type layout: QLayout
        :param take: Индекс элементов, которые будут удаляться
        :type take: int
        :param hidden: Флаг для сокрытия виджетов, которым мало удаления
        :type hidden: bool
        """
        length = layout.count()
        for _ in range(length-1):
            item = layout.takeAt(take)
            if hidden:
                item.widget().hide()

    def openCatalog(self) -> NoReturn:
        """Работа со справочником изделий"""
        window = Catalog(self)
        window.show()

    def openSettings(self) -> NoReturn:
        """Работа с окном настроек"""
        window = Settings(self, self.settings)
        if window.exec_() == QDialog.Accepted:
            self.readSettings()

    def openNewOrder(self) -> NoReturn:
        """Добавление нового заказа

        Открывается диалоговое окно и если пользователь нажал <Добавить>,
        то необходимо будет добавить секцию заказа в список заказов на
        первую позицию
        """
        window = NewOrderDialog(self)
        if window.exec_() == QDialog.Accepted:
            order = window.getNewOrder()
            order_section = Section(order[0], order[1])
            order_section.setContentFields(
                self.createOrderTable(order[0], *order[2:])
            )
            order_section.clicked.connect(self.showOrderInformation)
            self.ui.scrollAreaWidgetContents.layout().insertWidget(
                0, order_section
            )

    def openCloseOrder(self) -> NoReturn:
        """Диалоговое окно завершения шага

        При завершении обычного <не последнего> шага заказа просто потребует
        ввести некоторые данные для продолжения работы. При достижении
        последнего шага уведомит о завершении заказа.
        """
        if self.current_order.isLast():
            QMessageBox.information(
                self,
                'Завершение заказа',
                f'Заказ {self.current_section.name} завершён!',
                QMessageBox.Ok
            )
            self.closeCurrentOrder()
        else:
            # TODO: Божественный мисснейминг, это не окно завершения заказа,
            #       а окно завершения шага
            window = CloseOrderDialog(self)
            window.setWindowTitle(self.ui.closeOrder.text())
            if window.exec_() == QDialog.Accepted:
                depth = self.current_order.toNextDepth()
                # TODO: переключение вкладки после перехода на следующий шаг
                self.ui.closeOrder.setText('Завершить ' + str(depth) + ' мм')

    def closeCurrentOrder(self) -> NoReturn:
        """Закрытие текущего заказа

        Удаление секции с текущим заказом и создание новой секции того же
        заказа с новыми параметрами. Обновление данных о заказе в базе данных.
        Возврат на начальную страницу.
        """
        order = self.current_order.drop()
        StandardDataService.update_record(
            'orders',
            {'order_id': order[0]},
            status_id=4,
            current_depth=None,
            efficiency=order[4]
        )
        order_section = Section(order[0], order[1])
        order_section.setContentFields(
            self.createOrderTable(order[0], order[2], order[3], None, order[4])
        )
        order_section.clicked.connect(self.showOrderInformation)
        self.ui.scrollAreaWidgetContents.layout().insertWidget(
            0, order_section
        )
        self.ui.verticalLayout_8.removeWidget(self.current_section)
        self.current_section.hide()
        self.ui.mainArea.setCurrentIndex(0)
        self.ui.orderInformationArea.setCurrentIndex(0)
        self.ui.information.setChecked(True)

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
        self.cutting_thickness = self.settings.value(
            'cutting/cutting_thickness', defaultValue=4.2, type=float)

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
            'cutting/cutting_thickness', self.cutting_thickness)

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


class OrderContext:

    def __init__(self):
        self.id: int = 0
        self.name: str = ''
        self.st_name: str = ''
        self.st_id: int = 1
        self.ingots: list = []
        self.__complects: dict = {}
        self.amount: int = 0
        self.depth_list: list = []
        self.depth_ptr: int = 0
        self.efficiency: float = 0.0

        self.root = None

    @property
    def complects(self) -> dict:
        return self.__complects

    @complects.setter
    def complects(self, value: dict) -> NoReturn:
        self.__complects = value
        self.amount = len(value)

    @property
    def tree(self):
        # TODO: переделать в возврат итерируемой коллекции, через которую
        #       я и сделаю дерево карты раскроя
        return self.root

    @tree.setter
    def tree(self, value: BinNode):
        self.root = value
        self.root.update_size()
        leaves: list[CuttingChartNode] = self.root.cc_leaves
        leaves.sort(key=attrgetter('bin.height'), reverse=True)
        self.depth_list = [leave.bin.height for leave in leaves]

    @property
    def depth(self):
        return self.depth_list[self.depth_ptr]

    @depth.setter
    def depth(self, value: float):
        if value in self.depth_list:
            self.depth_ptr = self.depth_list.index(value)
        else:
            self.depth_ptr = 0

    def depth_index(self, depth: float):
        if depth in self.depth_list:
            return self.depth_list.index(depth)
        return -1

    def isLast(self):
        return self.depth_ptr + 1 == len(self.depth_list)

    def toNextDepth(self):
        self.depth_ptr = (self.depth_ptr + 1) % len(self.depth_list)
        StandardDataService.update_record(
            'orders',
            {'order_id': self.order_id},
            current_depth=self.depth
        )

    def drop(self):
        data = [
            self.id, self.name, self.amount, "Завершён, укомплектован",
            self.efficiency
        ]
        self.id = 0
        self.name = ''
        self.st_name = ''
        self.st_id = 1
        self.ingots = []
        self.__complects = {}
        self.amount = 0
        self.depth_list = []
        self.depth_ptr = 0
        self.efficiency = 0.0
        self.root = None

        return data


if __name__ == '__main__':
    application = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(application.exec_())
