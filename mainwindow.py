import sys
import pickle
import logging
import time
from typing import Iterable, Union
from itertools import chain
from operator import itemgetter
from collections import Counter, deque
from pathlib import Path

from PySide6.QtCore import Qt, QSettings, QModelIndex
from PySide6.QtWidgets import (
    QApplication, QGraphicsView, QMainWindow, QTableWidget, QTableWidgetItem,
    QTreeWidgetItem, QMessageBox, QDialog, QHBoxLayout, QVBoxLayout, QLayout,
    QGraphicsScene, QProgressDialog
)

from gui import ui_mainwindow, ui_full_screen
from gui.ui_functions import *

from widgets import IngotSectionDelegate, Section, ExclusiveButton, OrderSectionDelegate, Plate
from models import IngotModel, OrderModel
from charts.plan import CuttingPlanPainter, MyQGraphicsView
from charts.map import CuttingMapPainter

from sequential_mh.bpp_dsc.rectangle import (
    Direction, Material, Blank, Kit, Bin
)
from sequential_mh.bpp_dsc.tree import (
    BinNode, Tree, solution_efficiency, is_defective_tree, is_cc_node
)
from sequential_mh.bpp_dsc.prediction import optimal_ingot_size
from sequential_mh.bpp_dsc.support import dfs
from sequential_mh.bpp_dsc.stm import (
    _pack, _create_insert_template, predicate, is_empty_tree, is_empty_node
)

from service import (
    OrderDataService, FusionDataService, IngotsDataService, StandardDataService
)
from dialogs import OrderDialog, NewIngotDialog
from catalog import Catalog
from settings import SettingsDialog
from log import setup_logging, timeit


Number = Union[int, float]
Sizes = tuple[Number, Number, Number]
ListSizes = list[Sizes]


class FullScreenWindow (QDialog):
    def __init__(self, parent=None):
        super(FullScreenWindow, self).__init__(parent)
        self.ui = ui_full_screen.Ui_Dialog()
        self.ui.setupUi(self)

        self.setWindowFlags(Qt.Window)


class MainWindow (QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = ui_mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)

        # Установка визуальных дополнений приложения
        UIFunctions.setApplicationStyles(self)
        UIFunctions.setTopbarShadow(self)

        # Модель и делегат заказов
        self.order_model = OrderModel(self)
        self.order_delegate = OrderSectionDelegate(self.ui.searchResult_1)

        # Постраиваемое дерево раскроя
        self.tree = None

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
        self.map_scene = QGraphicsScene()
        self.graphicsView = MyQGraphicsView()
        self.graphicsView.setScene(self.plan_scene)
        self.graphicsView.setAlignment(Qt.AlignCenter)
        self.graphicsView.setDragMode(QGraphicsView.ScrollHandDrag)
        self.ui.chartArea.layout().addWidget(self.graphicsView)
        self.ui.graphicsView.setScene(self.map_scene)
        self.map_painter = CuttingMapPainter(self.map_scene)
        self.plan_painter = CuttingPlanPainter(self.plan_scene)

        # TODO: Пока без фактического режима эта кнопка не нужна.
        self.ui.closeOrder.hide()
        self.ui.searchNumber.hide()
        self.ui.searchType.hide()

        # Соединяем сигналы окна со слотами класса
        self.ui.newOrder.clicked.connect(self.openNewOrder)
        self.ui.catalog.clicked.connect(self.openCatalog)
        self.ui.settings.clicked.connect(self.openSettings)
        self.ui.newIngot.clicked.connect(self.openNewIngot)

        # Сигнал возврата на исходную страницу с информацией о заказах
        self.ui.information.clicked.connect(
            lambda: (
                self.ui.mainArea.setCurrentIndex(0),
                self.ui.information.setChecked(True),
                self.plan_painter.clearCanvas()
            )
        )
        self.ui.detailedPlan.clicked.connect(
            lambda: (
                self.ui.mainArea.setCurrentIndex(1),
                self.ui.chart.setChecked(True),
                self.chartPagePreparation()
            )
        )

        # Кнопку "Исходная пластина" привязываем отдельно от всех
        self.ui.sourcePlate.clicked.connect(self.depthLineChanged)

        # Кнопки страницы заказа
        self.ui.fullScreen.clicked.connect(self.openFullScreen)
        self.ui.saveComplect.clicked.connect(self.saveComplectsParameters)
        self.ui.recalculate.clicked.connect(self.createTree)
        self.ui.saveComplectAndRecreate.clicked.connect(self.safeCreateTree)

        # Сигнал делегата на удаление заказа из списка
        self.order_delegate.deleteIndexClicked.connect(self.deleteOrder)

        # Заполняем список заказов из базы
        self.loadOrderList()

    def loadOrderList(self):
        """Подгрузка списка заказов

        Загружается список заказов из таблицы заказов и на его основе
        формируется скомпонованный слой из виджетов Section с информацией.
        """
        self.order_model.setupModelData()
        self.ui.searchResult_1.setModel(self.order_model)
        self.ui.searchResult_1.setItemDelegate(self.order_delegate)
        self.ui.searchResult_1.clicked.connect(self.showOrderInformation)

    def refreshCompletcsTreeWidget(self, data: dict):
        self.ui.treeWidget.clear()
        for article, details in data['complects'].items():
            article_item = QTreeWidgetItem(
                self.ui.treeWidget, [article[1], None, None, None, None, None, None, str(article[0])])
            for detail in details:
                status_id = detail[-1]
                status = StandardDataService.get_by_id(
                    'complects_statuses', {'status_id': status_id}
                )
                detail_item = QTreeWidgetItem(
                    article_item, [detail[1], str(detail[4]),
                    str(detail[5]), str(detail[6]), str(detail[2]),
                    str(detail[3]), status[1], str(detail[0])]
                )
                for column in range(1, 6):
                    detail_item.setTextAlignment(column, Qt.AlignCenter)
                for column in range(0, 8):
                    detail_item.setBackground(column, QColor(status[2]))
                    detail_item.setForeground(column, QColor(status[3]))
                detail_item.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)
            self.ui.treeWidget.addTopLevelItem(article_item)
        self.ui.treeWidget.hideColumn(7)
        self.ui.treeWidget.expandAll()
        for column in range(7):
            self.ui.treeWidget.resizeColumnToContents(column)

    def showOrderInformation(self, index: QModelIndex):
        """Переключатель активных заказов и открытых секций

        Отвечает за то, чтобы одновременно была раскрыта только одна секция
        из списка заказов. Подгружает новую страницу заказа при его выборе.
        """
        if not index.isValid():
            return
        data_row = index.data(Qt.DisplayRole)
        
        self.ingot_model = IngotModel(order = data_row['order_id'])
        self.ingot_model.setupModelData()
        self.ingot_delegate = IngotSectionDelegate(self.ui.ingotsView)
        self.ui.ingotsView.setItemDelegate(self.ingot_delegate)
        self.ui.ingotsView.setModel(self.ingot_model)

        status = data_row['status_id']
        if status == 1 or status == 2:
            self.ui.label_5.hide()
            self.ui.label_6.hide()
        elif status == 4 or status == 5:
            self.ui.detailedPlan.hide()

        storage = ' (на склад)' if data_row['is_on_storage'] else ''
        self.ui.label.setText('Заказ ' + data_row['order_name'] + storage)

        self.map_scene.clear()

        self.refreshCompletcsTreeWidget(data_row)

        if self.is_file_exist(data_row):
            self.load_tree(data_row)
            self.map_painter.setTree(self.tree)
            self.map_painter.setEfficiency(data_row['efficiency'])
            self.map_painter.drawTree()

        self.ui.orderInformationArea.setCurrentWidget(self.ui.informationPage)

    def deleteOrder(self, index: QModelIndex):
        data_row = index.data(Qt.DisplayRole)
        answer = QMessageBox.question(
            self, 'Подтверждение удаления',
            f'Вы уверены, что хотите удалить заказ "{data_row["order_name"]}"?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
        )
        if answer == QMessageBox.Yes:
            success = StandardDataService.delete_by_id(
                'orders', {'order_id': data_row['order_id']}
            )
            if success:
                self.order_model.deleteRow(index.row())
                self.ui.orderInformationArea.setCurrentWidget(self.ui.defaultPage)
            else:
                QMessageBox.critical(
                    self, 'Ошибка удаления',
                    f'Не удалось удалить заказ "{data_row["order_name"]}"',
                    QMessageBox.Close, QMessageBox.Close
                )

    def updateDetailStatuses(self, data: dict):
        unplaced = list(chain.from_iterable([leave.result.unplaced for leave in self.tree.cc_leaves]))
        unplaced_counter = Counter([blank.name for blank in unplaced])
        complect_counter = {blank[1]: (blank[0], blank[2], blank[6], blank[7]) for blank in chain.from_iterable(data['complects'].values())}
        try:
            for name in unplaced_counter:
                detail_id, amount, depth, _ = complect_counter[name]
                surplus = unplaced_counter[name]
                print(name, amount, surplus)
                if amount == surplus:
                    OrderDataService.update_status(
                        {'order_id': data['order_id']},
                        {'detail_id': detail_id},
                        'status_id', 4
                    )
                else:
                    OrderDataService.update_status(
                        {'order_id': data['order_id']},
                        {'detail_id': detail_id},
                        'status_id', 5
                    )
            
            for name in complect_counter:
                detail_id, amount, depth, status_id = complect_counter[name]
                surplus = unplaced_counter[name]
                if status_id == 6:
                    continue

                if depth not in self.steps():
                    OrderDataService.update_status(
                        {'order_id': data['order_id']},
                        {'detail_id': detail_id},
                        'status_id', 4
                    )
                elif surplus == 0:
                    OrderDataService.update_status(
                        {'order_id': data['order_id']},
                        {'detail_id': detail_id},
                        'status_id', 1
                    )
        except Exception as e:
            print(e.args)
        current_index = self.ui.searchResult_1.currentIndex()
        self.order_model.setData(current_index, {'complects':  OrderDataService.complects({'order_id': data['order_id']})}, Qt.EditRole)
        self.refreshCompletcsTreeWidget(self.order_model.data(current_index, Qt.DisplayRole))

    def saveComplectsParameters(self):
        order_id = self.ui.searchResult_1.currentIndex().data(Qt.DisplayRole)['order_id']
        for i in range(self.ui.treeWidget.model().rowCount()):
            article_item = self.ui.treeWidget.topLevelItem(i)
            article_id = article_item.data(7, Qt.DisplayRole)
            for j in range(article_item.childCount()):
                detail_item = article_item.child(j)
                detail_id = detail_item.data(7, Qt.DisplayRole)
                # TODO: обрабатывать возможность неудачного сохранения, но пока
                #       я не знаю, как именно
                _ = OrderDataService.update_complect(
                    {'order_id': order_id},
                    {'article_id': article_id},
                    {'detail_id': detail_id},
                    amount=detail_item.data(4, Qt.DisplayRole),
                    priority=detail_item.data(5, Qt.DisplayRole),
                )

    def safeCreateTree(self):
        self.saveComplectsParameters()
        self.createTree()

    def openFullScreen(self):
        window = FullScreenWindow(self)
        window.ui.graphicsView.setScene(self.map_scene)
        window.setWindowTitle('Карта: полноэкранный режим')
        window.show()

    def createTree(self):
        # Пока работаем только с одном слитком
        data_row = self.ui.searchResult_1.currentIndex().data(Qt.DisplayRole)
        main_ingot = data_row['ingots'][0]
        main_ingot = [main_ingot[3], main_ingot[4], main_ingot[5], main_ingot[6]]

        # TODO: Вторым аргументом нужно вставить плотность сплава
        material = Material(main_ingot[0], 2.2, 1.)

        # Выбор заготовок и удаление лишних значений
        try:
            details_info = map(
                itemgetter(0), filter(lambda x: x[7] != 6, chain.from_iterable(data_row['complects'].values()))
            )
            details = self.getDetails(details_info, material)
        except Exception as e: 
            QMessageBox.critical(
                self,
                'Ошибка сборки',
                'Конфигурация заказа привела к сбою программы!\n'
                f'{e}',
                QMessageBox.Ok
            )
        progress = QProgressDialog('OCI', 'Закрыть', 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle('Раскрой')
        progress.forceShow()
        order_name = data_row['order_name']
        try:
            progress.setLabelText('Процесс раскроя...')
            logging.info(
                'Попытка создания раскроя для заказа %(name)s.',
                {'name': order_name}
            )
            size = main_ingot[1:]
            logging.info(
                'Заказ %(name)s: %(blanks)d заготовок, %(heights)d толщин, '
                'слиток %(length)dх%(width)dх%(height)d',
                {
                    'name': order_name, 'blanks': details.qty(),
                    'heights': len(details.keys()),
                    'length': size[0], 'width': size[1], 'height': size[2]
                }
            )
            self.createCut(size, details, material, progress=progress)
            logging.info(
                'Раскрой для заказа %(name)s успешно создан.',
                {'name': order_name}
            )
            progress.setLabelText('Завершение раскроя...')
        except Exception as e: 
            QMessageBox.critical(
                self,
                'Ошибка разреза',
                'Конфигурация заказа привела к сбою программы!\n'
                f'{e}',
                QMessageBox.Ok
            )
        progress.close()

        self.updateDetailStatuses(data_row)

        data_row = self.ui.searchResult_1.currentIndex().data(Qt.DisplayRole)
        StandardDataService.update_record(
            'orders', {'order_id': data_row['order_id']},
            efficiency=data_row['efficiency']
        )
        self.save_tree(data_row)

        self.map_scene.clear()
        self.map_painter.setTree(self.tree)
        self.map_painter.setEfficiency(data_row['efficiency'])
        self.map_painter.drawTree()

    def predict_size(self, material, kit):
        """Метод расчета параметров слитка"""
        # TODO: считать из настроек максимальные параметры слитка
        #       без припусков на фрезеровку и погрешность!
        max_size = (180, 180, 30)
        # max_length = 180
        # max_width = 180
        # max_height = 30
        bin_ = Bin(*max_size, material=material)
        root = BinNode(bin_, kit=kit)
        tree = Tree(root)

        settings = {
            'max_size': (
                (self.maximum_plate_height, self.clean_roll_plate_width),
                (self.maximum_plate_height, self.rough_roll_plate_width)
            ),
            'cutting_length': self.guillotine_width,
            'cutting_thickness': round(self.cutting_thickness, 4),
            'hem_until_3': self.rough_roll_edge_loss,
            'hem_after_3': self.clean_roll_edge_loss,
            'allowance': self.cut_allowance,
            'end': round(self.end_face_loss, 4),
        }

        # TODO: считать из настроек минимальные параметры слитка
        #       без припусков на фрезеровку и погрешность!
        min_size = (70, 70, 20)
        # min_length = 180
        # min_width = 180
        # min_height = 30

        # Дерево с рассчитанным слитком
        tree = optimal_ingot_size(tree, min_size, max_size, settings)
        efficiency = solution_efficiency(tree.root, list(dfs(tree.root)), is_total=True)
        print(f'Эффективность после расчета: {efficiency}')

        # TODO: Получить из настроек погрешность и припуски на фрезеровку
        size_error = 2
        allowance = 1.5

        # Получение слитка с учетом погрешности и припусков
        length = tree.root.bin.length + size_error + 2 * allowance
        width = tree.root.bin.width + size_error + 2 * allowance
        height = tree.root.bin.height + size_error + 2 * allowance

        print(f'Финальные размеры: {length, width, height}')
        print(f'Масса слитка (в гр): {length * width * height * material.density / 1000}')
        print(f'Масса слитка (в кг): {length * width * height * material.density / 1_000_000}')
        print(f'{material.density = }')

    def getDetails(self, details_id: Iterable[int], material: Material) -> Kit:
        """Формирование набора заготовок

        :param details_id: Список id заготовок
        :type details_id: Iterable[int]
        :param material: Материал
        :type material: Material
        :return: Набор заготовок
        :rtype: Kit
        """
        data_row = self.ui.searchResult_1.currentIndex().data(Qt.DisplayRole)
        details = []
        for id_ in details_id:
            detail = OrderDataService.get_detail(
                {'order_id': data_row['order_id']},
                {'detail_id': id_}
            )
            amount = detail[0]
            size: Sizes = detail[1:4]

            # FIXME: Стоит оставить на всякий случай с нулевыми размерами
            if 0 in size:
                continue

            priority: int = detail[4]

            # FIXME: Оставить проверку на случай с аномальными направлениями
            direction: int = detail[5]
            direction = Direction(3) if direction == 1 else Direction(2)

            for _ in range(amount):
                blank = Blank(
                    *size, priority, direction=direction, material=material
                )
                blank.name = detail[6]
                details.append(blank)
        kit = Kit(details)
        kit.sort('width')
        return kit

    def createCut(self, ingot_size: Sizes, kit: Kit, material: Material, progress=None):
        """Метод запуска алоритма раскроя

        :param ingot_size: Размер слитка в формате (длина, ширина, толщина)
        :type ingot_size: tuple[Number, Number, Number]
        :param kit: Набор заготовок
        :type kit: Kit
        :param material: Материал
        :type material: Material
        """
        # self.current_order.save_tree()
        settings = {
            'max_size': (
                (self.maximum_plate_height, self.clean_roll_plate_width),
                (self.maximum_plate_height, self.rough_roll_plate_width)
            ),
            'cutting_length': self.guillotine_width,
            'cutting_thickness': round(self.cutting_thickness, 4),
            'hem_until_3': self.rough_roll_edge_loss,
            'hem_after_3': self.clean_roll_edge_loss,
            'allowance': self.cut_allowance,
            'end': round(self.end_face_loss, 4),
        }
        bin_ = Bin(*ingot_size, material=material)
        root = BinNode(bin_, kit=kit)
        tree = Tree(root)
        tree = self.stmh_idrd(tree, restrictions=settings, progress=progress)
        self.tree = tree.root

        # считаем эффективность со всего слитка (в долях!)
        # для отображения нужно округлить!
        current_index = self.ui.searchResult_1.currentIndex()
        self.order_model.setData(current_index, {'efficiency': round(100 * solution_efficiency(
            self.tree, list(dfs(tree.root)), is_total=True), 2)}, Qt.EditRole)

    # Методы из пакета sequential_mh.bpp_dsc
    # перенесены для возможности учета прогрогресса
    @timeit
    def stmh_idrd(self, tree, with_filter=True, restrictions=None, progress=None):
        is_main = True
        trees = self._stmh_idrd(
            tree, restrictions=restrictions, local=not is_main,
            with_filter=with_filter, progress=progress
        )

        if restrictions:
            max_size = restrictions.get('max_size')
        else:
            max_size = None
        print(f'Количество деревьев: {len(trees)}')
        progress.setLabelText('Фильтрация решений...')
        if with_filter:
            trees = [
                item for item in trees if not is_defective_tree(item, max_size)
            ]

        print(f'Годных деревьев: {len(trees)}')
        progress.setLabelText('Выбор оптимального решения...')
        best = max(
            trees, key=lambda item: solution_efficiency(
                item.root, list(dfs(item.root)), nd=True, is_p=True
            )
        )
        total_efficiency = solution_efficiency(best.root, list(dfs(best.root)), is_total=True)
        print('Построение дерева завершено')
        print(f'Общая эффективность: {total_efficiency:.4f}')
        print(f'Взвешенная эффективность: {solution_efficiency(best.root, list(dfs(best.root)), nd=True):.4f}')
        print(f'Эффективность с приоритетами: {solution_efficiency(best.root, list(dfs(best.root)), is_p=True):.4f}')
        print('-' * 50)
        return best

    def _stmh_idrd(self, tree, local=False, with_filter=True, restrictions=None, progress=None):
        level = deque([tree])
        result = []
        step = 0
        doubling = False
        if restrictions:
            cut_thickness = restrictions.get('cutting_thickness')
            doubling = cut_thickness >= max(tree.root.kit.keys())
        steps = number_of_steps(len(tree.root.kit.keys()), doubling=doubling)
        progress.setRange(0, steps)

        if restrictions:
            max_size = restrictions.get('max_size')
        else:
            max_size = None

        while level:
            step += 1
            new_level = deque([])
            for _, tree_ in enumerate(level):
                if with_filter and is_defective_tree(tree_, max_size=max_size):
                    # Додумать на сколько уменьшать
                    # min_height = min(map(lambda item: item.bin.height, tree_.root.cc_leaves))
                    # steps -= number_of_steps(len([x for x in tree.root.kit.keys() if x < min_height]), doubling=False)
                    steps -= 1
                    progress.setRange(0, steps)
                    progress.setValue(step - 1)
                    continue
                if is_empty_tree(tree_):
                    result.append(tree_)
                else:
                    new_level.append(tree_)
            level = new_level
            if not level:
                break

            tree = level.popleft()
            nodes = [
                node for node in tree.root.leaves() if not is_empty_node(node)
            ]
            nodes = deque(sorted(nodes, key=predicate))
            node = nodes[0]
            if is_cc_node(node):
                _pack(node, level, restrictions)
                if is_empty_tree(tree):
                    result.append(tree)
                else:
                    level.append(tree)
            else:
                _create_insert_template(node, level, tree, local, restrictions)
            if progress:
                # print(step, steps)
                progress.setValue(step)

        # костыль для завершения прогресса
        if step < steps and progress:
            progress.setValue(steps)

        return result

    def steps(self):
        leaves = self.tree.cc_leaves
        depth_list = [leave.bin.height for leave in leaves]
        return depth_list

    def chartPagePreparation(self):
        """Подготовка страницы с планами раскроя

        Подгрузка списка заготовок, формирование кнопок толщин.
        """
        data_row = self.ui.searchResult_1.currentIndex().data(Qt.DisplayRole)
        self.clearLayout(self.ui.horizontalLayout_6, take=1)
        for depth in self.steps():
            button = ExclusiveButton(depth=depth)
            button.clicked.connect(self.depthLineChanged)
            self.ui.horizontalLayout_6.addWidget(button)
        self.ui.horizontalLayout_6.addStretch()
        self.ui.sourcePlate.setChecked(True)

        self.sourcePage()

        # Кнопку заверешния заказа меняем на кнопку перехода на след.шаг
        depth = data_row['current_depth']
        self.ui.closeOrder.setText('Завершить ' + str(depth) + ' мм')

    def depthLineChanged(self):
        """Просмотр другой толщины и подгрузка нового списка деталей"""
        button = self.sender()
        self.plan_painter.clearCanvas()
        self.graphicsView.viewport().update()
        self.graphicsView.verticalScrollBar().setValue(
            self.graphicsView.verticalScrollBar().minimum()
        )
        if button is self.ui.sourcePlate:
            self.sourcePage()
        else:
            depth = button.depth
            self.stepPage(depth)

    def sourcePage(self):
        """Переход на страницу с исходным слитком"""
        self.loadDetailList(depth=0.0)
        self.graphicsView.setScene(self.map_scene)

    def stepPage(self, depth: float):
        data_row = self.ui.searchResult_1.currentIndex().data(Qt.DisplayRole)
        self.graphicsView.setScene(self.plan_scene)
        index = self.steps().index(depth)
        pack = self.tree.cc_leaves[index]
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
        self.loadDetailList(depth=float(depth))

    def loadDetailList(self, depth: float):
        """Подгрузка списка заготовок

        Список заготовок конкретной толщины, если выбрана толщина, но
        полный список всех заготовок заказа, если выбрана <Исходная пластина>.
        """
        data_row = self.ui.searchResult_1.currentIndex().data(Qt.DisplayRole)
        self.clearLayout(self.ui.verticalLayout_8, hidden=True)
        cut_blanks = OrderDataService.cut_blanks({'order_id': data_row['order_id']}, depth)
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

    def clearLayout(self, layout: QLayout, take: int = 0, hidden: bool = False, last: int = 1):
        """Метод для очистки слоёв компановки

        :param layout: Слой с которого удаляются виджеты по заданным правилам
        :type layout: QLayout
        :param take: Индекс элементов, которые будут удаляться
        :type take: int
        :param hidden: Флаг для сокрытия виджетов, которым мало удаления
        :type hidden: bool
        """
        length = layout.count()
        for _ in range(length-last):
            item = layout.takeAt(take)
            if hidden or isinstance(item.widget(), ExclusiveButton):
                item.widget().hide()

    def openCatalog(self):
        """Работа со справочником изделий"""
        window = Catalog(self)
        window.show()

    def openSettings(self):
        """Работа с окном настроек"""
        window = SettingsDialog(self, self.settings)
        if window.exec_() == QDialog.Accepted:
            self.readSettings()

    def openNewIngot(self):
        window = NewIngotDialog(self)

        fusions_list = FusionDataService.fusions_list()
        window.setFusionsList(fusions_list)

        window.exec_()

    def openNewOrder(self):
        """Добавление нового заказа

        Открывается диалоговое окно и если пользователь нажал <Добавить>,
        то необходимо будет добавить секцию заказа в список заказов на
        первую позицию
        """
        if not IngotsDataService.vacancy_ingots():
            QMessageBox.critical(
                self,
                'Ошибка добавления',
                'Отсутствуют свободные слитки\nНевозможно добавить заказ.',
                QMessageBox.Ok
            )
        else:
            window = OrderDialog(self)
            if window.exec_() == QDialog.Accepted:
                order = window.getNewOrder()
                self.order_model.appendRow(order)

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

    def save_tree(self, data: dict):
        """Сохранение корневого узла дерева"""
        file_name = self.get_file_name(data)
        path = 'schemes'
        abs_path = get_abs_path(file_name, path)
        with abs_path.open(mode='wb') as f:
            pickle.dump(self.tree, f)
            print('Файл сохранен')

    def is_file_exist(self, data: dict):
        file_name = self.get_file_name(data)
        path = 'schemes'
        abs_path = get_abs_path(file_name, path)
        return abs_path.exists()

    def load_tree(self, data: dict):
        """Загрузка корневого узла дерева из файла"""
        file_name = self.get_file_name(data)
        path = 'schemes'
        abs_path = get_abs_path(file_name, path)
        with abs_path.open(mode='rb') as f:
            self.tree = pickle.load(f)
            print(f'Файл считан: {self.tree}')

    def get_file_name(self, data: dict) -> str:
        """Создание имени файла для сохранения дерева раскроя"""
        extension = 'oci'
        return f'{data["order_id"]}_{data["creation_date"]}.{extension}'


def get_abs_path(file_name, path=None) -> Path:
    # file_name = self.get_file_name()
    # path = 'schemes'
    # Path.cwd() ?
    # dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
    dir_path = Path(__file__).parent.absolute()
    if path:
        abs_path = dir_path / path / file_name
    else:
        abs_path = dir_path / file_name
    return abs_path


def number_of_steps(num_of_heights, doubling=True):
    """Количество шагов алгоритма

    :param num_of_heights: Количество толщин
    :type num_of_heights: int
    :param doubling: Использование удвоения, когда используется толщина
                     реза, defaults to True
    :type doubling: bool, optional
    :return: Количество операций в алгоритме
    :rtype: int
    """
    number_of_trees = 4 * (4 ** num_of_heights - 1) / 3
    if doubling:
        number_of_trees *= 2
        n = (4 ** num_of_heights * 2 - 2) / 3 + 1
    else:
        n = (4 ** num_of_heights - 1) / 3 + 1
    return int(number_of_trees + n)


if __name__ == '__main__':
    oci_logger = setup_logging()
    logging.info('Приложение OCI запущено.')
    start = time.time()
    application = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    exit_code = application.exec_()

    total_time = time.time() - start
    print(f'{start = }, {total_time = }')
    logging.info(
        'Выход из приложения OCI. Время работы: %(time).2f мин.',
        {'time': total_time / 60}
    )

    sys.exit(exit_code)
