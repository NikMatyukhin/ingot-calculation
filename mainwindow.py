import sys
import pickle
import logging
import time
from typing import Dict, Union
from itertools import chain
from collections import Counter, deque
from pathlib import Path

from PySide6.QtCore import (
    Qt, QSettings, QModelIndex
)
from PySide6.QtWidgets import (
    QApplication, QGraphicsView, QMainWindow, QTableWidget, QTableWidgetItem,
    QMessageBox, QDialog, QVBoxLayout, QGraphicsScene, QLayout, QProgressDialog
)

from gui import ui_mainwindow
from gui.ui_functions import *
from widgets import (
    IngotSectionDelegate, Section, ExclusiveButton, OrderSectionDelegate
)
from models import (
    IngotModel, OrderInformationComplectsModel, OrderModel
)
from service import (
    OrderDataService, StandardDataService
)
from dialogs import (
    IngotAddingDialog, IngotReadinessDialog, OrderAddingDialog, FullScreenWindow
)
from charts.plan import CuttingPlanPainter, MyQGraphicsView
from charts.map import CuttingMapPainter
from catalog import Catalog
from settings import SettingsDialog
from exceptions import ForcedTermination
from log import setup_logging, timeit

from sequential_mh.bpp_dsc.rectangle import (
    Direction, Material, Blank, Kit, Bin
)
from sequential_mh.bpp_dsc.tree import (
    BinNode, Tree, solution_efficiency, is_defective_tree, is_cc_node
)
from sequential_mh.bpp_dsc.support import dfs
from sequential_mh.bpp_dsc.stm import (
    _pack, _create_insert_template, predicate, is_empty_tree, is_empty_node
)


Number = Union[int, float]
Sizes = tuple[Number, Number, Number]
ListSizes = list[Sizes]


class OCIMainWindow(QMainWindow):

    def __init__(self):
        super(OCIMainWindow, self).__init__()
        self.ui = ui_mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)

        # Установка визуальных дополнений приложения
        UIFunctions.setApplicationStyles(self)
        UIFunctions.setTopbarShadow(self)

        # Модель и делегат заказов
        self.order_model = OrderModel(self)
        self.order_delegate = OrderSectionDelegate(self.ui.searchResult_1)
        self.ui.searchResult_1.setModel(self.order_model)
        self.ui.searchResult_1.setItemDelegate(self.order_delegate)
        self.order_delegate.deleteIndexClicked.connect(self.confirm_order_removing)

        # Модель слитков (обновляется при изменении текущего заказа)
        # TODO: пока заказ не выбран пусть содержит свободные слитки,
        #       чтобы потом показывать их на главном экране
        self.ingot_model = IngotModel()
        self.ingot_delegate = IngotSectionDelegate(self.ui.ingotsView)
        self.ui.ingotsView.setModel(self.ingot_model)
        self.ui.ingotsView.setItemDelegate(self.ingot_delegate)
        self.ui.ingotsView.clicked.connect(self.show_ingot_information)
        self.ingot_delegate.forgedIndexClicked.connect(self.confirm_ingot_readiness)

        # Модель комплектов (обновляется при изменении текущего заказа)
        # Не содержит ничего, пока не установлен идентификатор заказа
        self.complect_headers = [
            'Название', 'ID', 'Статус', 'Сплав', 'Длина', 'Ширина', 'Толщина',
            'Количество', 'Приоритет', 'Направление проката'
        ]
        self.complect_model = OrderInformationComplectsModel(self.complect_headers)
        self.ui.complectsView.setModel(self.complect_model)
        self.complect_model.dataChanged.connect(self.complect_changed)

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

        self.read_settings()

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
        self.ui.newOrder.clicked.connect(self.open_order_dialog)
        self.ui.catalog.clicked.connect(self.open_catalog_window)
        self.ui.settings.clicked.connect(self.open_settings_dialog)
        self.ui.newIngot.clicked.connect(self.open_ingot_dialog)

        # Сигнал возврата на исходную страницу с информацией о заказах
        self.ui.information.clicked.connect(
            lambda: (
                self.ui.mainArea.setCurrentIndex(0),
                self.ui.chart.setHidden(True),
                self.ui.information.setChecked(True),
                self.plan_painter.clearCanvas()
            )
        )
        self.ui.detailedPlan.clicked.connect(
            lambda: (
                self.ui.mainArea.setCurrentIndex(1),
                self.ui.chart.setHidden(False),
                self.ui.chart.setChecked(True),
                self.chartPagePreparation()
            )
        )

        # Показ текущего заказа по выбору
        self.ui.searchResult_1.clicked.connect(self.show_order_information)

        # Кнопку "Исходная пластина" привязываем отдельно от всех
        self.ui.sourcePlate.clicked.connect(self.depthLineChanged)

        # Кнопки страницы заказа
        self.ui.fullScreen.clicked.connect(self.open_fullscreen_window)
        self.ui.saveComplect.clicked.connect(self.save_complects)
        self.ui.recalculate.clicked.connect(self.create_tree)
        self.ui.saveComplectAndRecreate.clicked.connect(self.safe_create_tree)

    def show_order_information(self, index: QModelIndex):
        """Переключатель активных заказов и открытых секций.

        Отвечает за то, чтобы одновременно была раскрыта только одна секция
        из списка заказов. Подгружает новую страницу заказа при его выборе.
        """
        if not index.isValid():
            return
        current_order = index.data(Qt.DisplayRole)
        
        self.ingot_model.order = current_order['order_id']
        self.ui.ingotsView.setCurrentIndex(self.ingot_model.index(0, 0, QModelIndex()))
        self.show_ingot_information(self.ui.ingotsView.currentIndex())
        self.complect_model.order = current_order['order_id']
        for column in range(self.complect_model.columnCount(QModelIndex())):
            self.ui.complectsView.resizeColumnToContents(column)
        self.ui.complectsView.setColumnHidden(1, True)
        self.ui.complectsView.setColumnWidth(2, 100)
        self.ui.complectsView.setColumnWidth(3, 100)
        self.ui.complectsView.expandAll()

        status = current_order['status_id']
        if status == 1 or status == 2:
            self.ui.label_5.hide()
            self.ui.label_6.hide()
        elif status == 4 or status == 5:
            self.ui.detailedPlan.hide()

        self.ui.label.setText('Заказ ' + current_order['order_name'])

        self.map_scene.clear()
        
        current_ingot = self.ui.ingotsView.currentIndex().data(Qt.DisplayRole)
        if self.is_file_exist(current_order, current_ingot):
            self.load_tree(current_order, current_ingot)
            self.redraw_map(current_ingot)

        self.ui.orderInformationArea.setCurrentWidget(self.ui.informationPage)

    def show_ingot_information(self, current: QModelIndex):
        current_ingot = current.data(Qt.DisplayRole)
        current_order = self.ui.searchResult_1.currentIndex().data(Qt.DisplayRole)
        if current_ingot['status_id'] == 3:
            self.ui.recalculate.setEnabled(False)
        else:
            self.ui.recalculate.setEnabled(True)
        if self.is_file_exist(current_order, current_ingot):
            self.load_tree(current_order, current_ingot)
            self.redraw_map(current_ingot)
        else:
            self.map_scene.clear()

    def confirm_ingot_readiness(self, index: QModelIndex):
        """Подтверждение готовности слитка.

        :param index: Индекс подтверждаемого слитка
        :type index: QModelIndex
        """
        planned_ingot = self.ingot_model.data(index, Qt.DisplayRole)
        fusion_name = index.model().extradata(index, Qt.DisplayRole, 'fusion_name')
        sizes = planned_ingot['ingot_size']
        # Запрос данных о готовности слитка
        window = IngotReadinessDialog(self)
        # Установка заголовочных данных (размеры и сплав)
        window.set_title_data(planned_ingot['ingot_id'], sizes, fusion_name)
        if window.exec_() == QDialog.Accepted:
            # Заказ возможно стоит сделать обычным и готовым
            self.ingot_model.setData(index, {'status_id': 1, 'ingot_part': window.get_batch()}, Qt.EditRole)
            self.check_current_order()

    def check_current_order(self):
        """Проверка текущего заказа с возможным изменением статуса"""
        for row in range(self.ingot_model.rowCount()):
            ingot_index = self.ingot_model.index(row, 0, QModelIndex())
            ingot = self.ingot_model.data(ingot_index, Qt.DisplayRole)
            # Если есть запланированный слиток, то и заказ остаётся таким
            if ingot['status_id'] == 3:
                break
        # Если запланированных слитков не было и заказ готов к началу
        else:
            order_index = self.ui.searchResult_1.currentIndex()
            self.order_model.setData(order_index, {'status_id': 1}, Qt.EditRole)
            StandardDataService.update_record(
                'orders',
                {'order_id': order_index.data(Qt.DisplayRole)['order_id']},
                status_id=1
            )

    def confirm_order_adding(self, data: Dict):
        self.order_model.appendRow(data)

    def confirm_order_removing(self, index: QModelIndex):
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
                    QMessageBox.Close
                )

    def complect_changed(self, index: QModelIndex):
        text = self.ui.saveComplect.text()
        if not text.endswith('*'):
            self.ui.saveComplect.setText(text + '*')

    def update_complect_statuses(self, order_id: int, fusion_id: int):
        # Подсчитываем количество неразмещенных заготовок (название: количество)
        # FIXME: проблемы со статусами при наличии одинаковых веток
        #        эта фигня сама как-то работает, при обнаружении
        #        проблемы нужно вернуться
        # from itertools import groupby
        # from collections import Counter
        # from operator import attrgetter
        # unplaced = []
        # for height, group in groupby(self.tree.cc_leaves, key=attrgetter('bin.height')):
        #     group = list(group)
        #     num_leaves = len(group)
        #     blanks = list(chain.from_iterable([leave.result.unplaced for leave in group]))
        #     unplaced_for_group = list(filter(lambda item: item[1] == num_leaves, Counter(blanks).items()))
        #     unplaced.extend(unplaced_for_group)
        unplaced = list(chain.from_iterable([leave.result.unplaced for leave in self.tree.cc_leaves]))
        unplaced_counter = Counter([blank.name for blank in unplaced])

        # Переходим по всем изделиям в заказе
        model = self.complect_model
        complect_counter = {}
        for row in range(model.rowCount(QModelIndex())):
            parent = model.index(row, 0, QModelIndex())
            parent_name = model.data(parent, Qt.DisplayRole)
            # Переходим по всем заготовкам в изделии
            for sub_row in range(model.rowCount(parent)):
                detail_fusion = model.realdata(model.index(sub_row, 3, parent), Qt.DisplayRole)
                # Если не совпадают сплав заготовки и выбранного слитка - пропускаем
                if int(detail_fusion) != int(fusion_id):
                    continue
                # Собираем все нужные данные по колонкам
                name: str = model.data(model.index(sub_row, 0, parent), Qt.DisplayRole)
                detail_id: int = model.data(model.index(sub_row, 1, parent), Qt.DisplayRole)
                status_id_index = model.index(sub_row, 2, parent)
                depth: float = model.data(model.index(sub_row, 6, parent), Qt.DisplayRole)
                amount: int = model.data(model.index(sub_row, 7, parent), Qt.DisplayRole)
                complect_counter[parent_name + '_' + name] = {
                    'detail_id': detail_id,
                    'depth': float(depth),
                    'amount': int(amount),
                    'status_id': status_id_index
                }
        # Сначала проходимся по счётчику неразмещённых заготовок
        for name in unplaced_counter:
            # Если количество заготовок совпадает с остатком
            if complect_counter[name]['amount'] == unplaced_counter[name]:
                # Заготовка <не упакована>
                success = OrderDataService.update_status(
                    {'order_id': order_id},
                    {'detail_id': complect_counter[name]['detail_id']},
                    'status_id', 4
                )
                if success: model.setData(complect_counter[name]['status_id'], 4, Qt.EditRole)
            # Есди количество заготовок не совпадает с остатком
            else:
                # Заготовка <частично упакована>
                success = OrderDataService.update_status(
                    {'order_id': order_id},
                    {'detail_id': complect_counter[name]['detail_id']},
                    'status_id', 5
                )
                if success: model.setData(complect_counter[name]['status_id'], 5, Qt.EditRole)
        # В конце проходимся по всем заготовкам чтобы найти пропущенные толщины
        for name in complect_counter:
            if complect_counter[name]['depth'] not in self.steps():
                success = OrderDataService.update_status(
                    {'order_id': order_id},
                    {'detail_id': complect_counter[name]['detail_id']},
                    'status_id', 4
                )
                if success: model.setData(complect_counter[name]['status_id'], 4, Qt.EditRole)
            # Если количесво неразмещённых заготовок равно нулю
            elif name not in unplaced_counter:
                # Заготовка <ожидает>
                success = OrderDataService.update_status(
                    {'order_id': order_id},
                    {'detail_id': complect_counter[name]['detail_id']},
                    'status_id', 1
                )
                if success: model.setData(complect_counter[name]['status_id'], 1, Qt.EditRole)

    def save_complects(self):
        text = self.ui.saveComplect.text()
        if text.endswith('*'):
            order_id = self.ui.searchResult_1.currentIndex().data(Qt.DisplayRole)['order_id']
            model = self.complect_model
            
            for row in range(model.rowCount(QModelIndex())):
                article_index = model.index(row, 1, QModelIndex())
                article_id = model.data(article_index, Qt.DisplayRole)
            
                # HACK: без этого не работает
                article_index = model.index(row, 0, QModelIndex())
            
                for sub_row in range(model.rowCount(article_index)):
                    detail_index = model.index(sub_row, 1, article_index)
                    amount_index = model.index(sub_row, 7, article_index)
                    priority_index = model.index(sub_row, 8, article_index)
            
                    detail_id = model.data(detail_index, Qt.DisplayRole)
                    OrderDataService.update_complect(
                        {'order_id': order_id},
                        {'article_id': article_id},
                        {'detail_id': detail_id},
                        amount = model.data(amount_index, Qt.DisplayRole),
                        priority = model.data(priority_index, Qt.DisplayRole),
                    )
            self.ui.saveComplect.setText(text[:-1])

    def safe_create_tree(self):
        self.save_complects()
        self.create_tree()

    def create_tree(self):
        # Пока работаем только с одном слитком
        current_order = self.ui.searchResult_1.currentIndex().data(Qt.DisplayRole)
        current_ingot = self.ui.ingotsView.currentIndex().data(Qt.DisplayRole)
        fusion_name = self.ingot_model.extradata(self.ui.ingotsView.currentIndex(), Qt.DisplayRole, 'fusion_name')

        # TODO: Вторым аргументом нужно вставить плотность сплава
        material = Material(fusion_name, 2.2, 1.)

        # Выбор заготовок и удаление лишних значений
        details = None
        try:
            details = self.get_details_kit(material)
        except Exception as exception: 
            QMessageBox.critical(self, 'Ошибка сборки', f'{exception}', QMessageBox.Ok)
        # Отображение прогресса раскроя
        progress = QProgressDialog('OCI', 'Закрыть', 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle('Раскрой')
        progress.forceShow()
        order_name = current_order['order_name']
        ingot_size = current_ingot['ingot_size']
        logging.info(
            'Попытка создания раскроя для заказа %(name)s.',
            {'name': order_name}
        )
        progress.setLabelText('Процесс раскроя...') 
        try:
            logging.info(
                'Заказ %(name)s: %(blanks)d заготовок, %(heights)d толщин, '
                'слиток %(length)dх%(width)dх%(height)d',
                {
                    'name': order_name, 'blanks': details.qty(),
                    'heights': len(details.keys()),
                    'length': ingot_size[0], 'width': ingot_size[1], 'height': ingot_size[2]
                }
            )
            self.create_cut(ingot_size, details, material, progress=progress)
        except ForcedTermination:
            logging.info(
                'Раскрой для заказа %(name)s прерван пользователем.',
                {'name': order_name}
            )
            QMessageBox.information(self, 'Внимание', 'Процесс раскроя был прерван!', QMessageBox.Ok)
        except Exception as exception: 
            QMessageBox.critical(
                self, 'Раскрой завершился с ошибкой', f'{exception}', QMessageBox.Ok
            )
        else:
            progress.setLabelText('Завершение раскроя...')
            logging.info(
                'Раскрой для заказа %(name)s успешно создан.',
                {'name': order_name}
            )
        progress.close()

        current_order = self.ui.searchResult_1.currentIndex().data(Qt.DisplayRole)
        current_ingot = self.ui.ingotsView.currentIndex().data(Qt.DisplayRole)
        self.update_complect_statuses(current_order['order_id'], current_ingot['fusion_id'])
        self.save_tree(current_order, current_ingot)
        self.redraw_map(current_ingot)

    def redraw_map(self, ingot: Dict):
        self.map_scene.clear()
        self.map_painter.setTree(self.tree)
        self.map_painter.setEfficiency(ingot['efficiency'])
        self.map_painter.drawTree()

    def get_details_kit(self, material: Material) -> Kit:
        """Формирование набора заготовок

        :param material: Материал
        :type material: Material
        :return: Набор заготовок
        :rtype: Kit
        """
        model = self.complect_model
        details = []
        # Переходим по всем изделиям в заказе
        for row in range(model.rowCount(QModelIndex())):
            parent = model.index(row, 0, QModelIndex())
            parent_name = model.data(parent, Qt.DisplayRole)
            # Переходим по всем заготовкам в изделии
            for sub_row in range(model.rowCount(parent)):
                detail_fusion = model.data(model.index(sub_row, 3, parent), Qt.DisplayRole)
                # Если не совпадают сплав заготовки и выбранного слитка - пропускаем
                if detail_fusion != material.name:
                    continue
                # Собираем все нужные данные по колонкам
                name: str = model.data(model.index(sub_row, 0, parent), Qt.DisplayRole)
                length = int(model.data(model.index(sub_row, 4, parent), Qt.DisplayRole))
                width = int(model.data(model.index(sub_row, 5, parent), Qt.DisplayRole))
                depth = float(model.data(model.index(sub_row, 6, parent), Qt.DisplayRole))
                sizes: Sizes = [length, width, depth]
                amount = int(model.data(model.index(sub_row, 7, parent), Qt.DisplayRole))
                priority = int(model.data(model.index(sub_row, 8, parent), Qt.DisplayRole))
                direction_id = int(model.realdata(model.index(sub_row, 9, parent), Qt.DisplayRole))
                direction_code = 3 if direction_id == 1 else 2
                direction = Direction(direction_code)
                # Создаём заготовки из полученных данных
                for _ in range(amount):
                    blank = Blank(*sizes, priority, direction=direction, material=material)
                    blank.name = parent_name + '_' + name
                    details.append(blank)
        # Пакуем набор и сортируем по толщине
        kit = Kit(details)
        kit.sort('width')
        return kit

    def create_cut(self, ingot_size: Sizes, kit: Kit, material: Material,
                   progress: QProgressDialog = None):
        """Метод запуска алоритма раскроя.

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
            ),
            'cutting_length': self.guillotine_width,
            'cutting_thickness': round(self.cutting_thickness, 4),
            'hem_until_3': self.rough_roll_edge_loss,
            'hem_after_3': self.clean_roll_edge_loss,
            'allowance': self.cut_allowance,
            'end': round(self.end_face_loss, 4),
        }
        ingot_bin = Bin(*ingot_size, material=material)
        tree = Tree(BinNode(ingot_bin, kit=kit))
        tree = self.stmh_idrd(tree, restrictions=settings, progress=progress)
        self.tree = tree.root

        ingot_index = self.ui.ingotsView.currentIndex()
        ingot_id = ingot_index.data(Qt.DisplayRole)['ingot_id']
        total_efficiency = 100 * solution_efficiency(self.tree, list(dfs(self.tree)), is_total=True)
        data = {'efficiency': round(total_efficiency, 2)}
        self.ingot_model.setData(ingot_index, data, Qt.EditRole)
        StandardDataService.update_record(
            'ingots', {'ingot_id': ingot_id}, efficiency=data['efficiency']
        )
        # TODO: теперь непонятно, что есть эффективность раскроя целого набора
        # self.order_model.setData(current_index, data, Qt.EditRole)
        # StandardDataService.update_record(
        #     'orders', {'order_id': current_index.data(Qt.DisplayRole)['order_id']},
        #     efficiency = data['efficiency']
        # )

    @timeit
    def stmh_idrd(self, tree, with_filter: bool = True,
                  restrictions: dict = None, progress: QProgressDialog = None):
        is_main = True
        trees = self._stmh_idrd(
            tree, restrictions=restrictions, local=not is_main,
            with_filter=with_filter, progress=progress
        )

        if restrictions:
            max_size = restrictions.get('max_size')
        else:
            max_size = None
        # print(f'Количество деревьев: {len(trees)}')
        progress.setLabelText('Фильтрация решений...')
        if with_filter:
            trees = [
                item for item in trees if not is_defective_tree(item, max_size)
            ]

        # print(f'Годных деревьев: {len(trees)}')
        progress.setLabelText('Выбор оптимального решения...')
        best = max(
            trees, key=lambda item: solution_efficiency(
                item.root, list(dfs(item.root)), nd=True, is_p=True
            )
        )
        total_efficiency = solution_efficiency(best.root, list(dfs(best.root)), is_total=True)
        # print('Построение дерева завершено')
        # (f'Общая эффективность: {total_efficiency:.4f}')
        # (f'Взвешенная эффективность: {solution_efficiency(best.root, list(dfs(best.root)), nd=True):.4f}')
        # print(f'Эффективность с приоритетами: {solution_efficiency(best.root, list(dfs(best.root)), is_p=True):.4f}')
        # print('-' * 50)
        return best

    def _stmh_idrd(self, tree, local: bool = False, with_filter: bool = True,
                   restrictions: dict = None,
                   progress: QProgressDialog = None, end_progress=True):
        """Последовательная древовидная метаэвристика.

        Построение деревьев растроя.

        :param tree: Начальное дерево
        :type tree: Tree
        :param local: Флаг локальной оптимизации, defaults to False
        :type local: bool, optional
        :param with_filter: Флаг фильтрации деревьев
                            на соответствие ограничениям, defaults to True
        :type with_filter: bool, optional
        :param restrictions: Словарь ограничений, defaults to None
        :type restrictions: dict, optional
        :param progress: Прогресс бар, defaults to None
        :type progress: QProgressDialog, optional
        :raises ForcedTermination: Исключение принудительного завершения
        :return: Набор построенных деревьев раскроя
        :rtype: list[Tree]
        """
        level = deque([tree])
        result = []
        step = 0
        point_counter = 2
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
                progress.setValue(step)
                progress.setLabelText('Процесс раскроя.' + '.' * point_counter + ' ' * (2 - point_counter))
                point_counter = (point_counter + 1) % 3
                # print(f'{progress.wasCanceled() = }')
                if progress.wasCanceled():
                    raise ForcedTermination('Процесс раскроя был прерван')

        # костыль для завершения прогресса
        if end_progress and step < steps and progress:
            progress.setValue(steps)

        return result

    def optimal_ingot_size(self, main_tree, min_size, max_size, restrictions, progress=None):
        """Определение размеров слитка

        :param main_tree: Основное дерево, содержащее слиток максимальных размеров
        :type main_tree: Tree
        :param min_size: Минимальные размеры слитка, (длина, ширина, высота)
        :type min_size: tuple[number, number, number]
        :param max_size: Максимальные размеры слитка, (длина, ширина, высота)
        :type max_size: tuple[number, number, number]
        :param restrictions: Ограничения
        :type restrictions: dict
        :raises ValueError: если построено некорректное дерево
        :return: Дерево раскроя для полученного слитка
        :rtype: Tree
        """
        min_length, min_width, min_height = min_size

        trees = self._stmh_idrd(
            main_tree, restrictions=restrictions, local=False,
            with_filter=False, progress=progress
        )

        for tree in trees:
            # Получение смежного остатка
            if len(tree.root.adj_leaves) > 1:
                raise ValueError('Смежных остатков более 1!')
            adj_node = tree.root.adj_leaves[0]
            # Обнуление размеров смежного остатка
            adj_node.bin.length = 0
            adj_node.bin.width = 0
            # Обновление размеров вышестоящих узлов:
            # Когда дошли до промежуточного узла:
            # обновлять размеры с учетом ограничений на размеры
            adj_node.upward_size_update(min_size=min_size, max_size=max_size)
            root_size = tree.root.bin.size
            if root_size[0] < min_length:
                tree.root.bin.length = min_length
            if root_size[1] < min_width:
                tree.root.bin.width = min_width
            if root_size[2] < min_height:
                tree.root.bin.height = min_height

            # TODO: Проблема в том, что тип разреза не обновляется
            # может случиться так, что резать нужно будет по другому! (в 7 примере)
            tree.root.update_size()

        if restrictions:
            max_leaf_size = restrictions.get('max_size')
        else:
            max_leaf_size = None
        trees = [
            item for item in trees if not is_defective_tree(item, max_leaf_size)
        ]
        best = max(
            trees,
            key=lambda item: solution_efficiency(
                item.root, list(dfs(item.root)), nd=True, is_p=True
            )
        )
        return best

    def steps(self):
        leaves = self.tree.cc_leaves
        depth_list = [leave.bin.height for leave in leaves]
        return depth_list

    def chartPagePreparation(self):
        """Подготовка страницы с планами раскроя"""
        # data_row = self.ui.searchResult_1.currentIndex().data(Qt.DisplayRole)
        self.clearLayout(self.ui.horizontalLayout_6, take=1)
        depth_list = self.steps()
        for i, depth in enumerate(depth_list):
            name = f'{depth} мм'
            if depth_list.count(depth) > 1:
                name += f' ({depth_list[:i].count(depth) + 1})'
            button = ExclusiveButton(depth=depth, name=name, index=i)
            button.clicked.connect(self.depthLineChanged)
            self.ui.horizontalLayout_6.addWidget(button)
        self.ui.horizontalLayout_6.addStretch()
        self.ui.sourcePlate.setChecked(True)

        self.sourcePage()

        # Кнопку заверешния заказа меняем на кнопку перехода на след.шаг
        # depth = data_row['current_depth']
        # self.ui.closeOrder.setText('Завершить ' + str(depth) + ' мм')

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
            index = button.index
            self.stepPage(index)

    def sourcePage(self):
        """Переход на страницу с исходным слитком"""
        self.loadDetailList(depth=0.0)
        self.graphicsView.setScene(self.map_scene)

    def stepPage(self, index: int):
        data_row = self.ui.searchResult_1.currentIndex().data(Qt.DisplayRole)
        self.graphicsView.setScene(self.plan_scene)
        pack = self.tree.cc_leaves[index]
        depth = pack.bin.height
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
        """Подгрузка списка заготовок"""
        # TODO: классика, переделать на model/view
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
        """Создание информационной таблички заготовки"""
        # TODO: когда будет model/view - удалю за ненужностью
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

        # TODO: удалить к херам и сделать по-человечески, а то по-дебильному
        # Линейно:
        # https://ru.stackoverflow.com/questions/607834/Удаление-виджетов-размещенных-в-qlayout
        # Рекурсивно:
        # https://stackoverflow.com/questions/4857188/clearing-a-layout-in-qt
        length = layout.count()
        for _ in range(length-last):
            item = layout.takeAt(take)
            if hidden or isinstance(item.widget(), ExclusiveButton):
                item.widget().hide()

    def open_fullscreen_window(self):
        """Просмотр карты в полноэкранном режиме"""
        window = FullScreenWindow(self)
        window.set_scene(self.map_scene)
        window.showMaximized()

    def open_catalog_window(self):
        """Работа со справочником изделий"""
        window = Catalog(self)
        window.showMaximized()

    def open_settings_dialog(self):
        """Работа с окном настроек"""
        window = SettingsDialog(self, self.settings)
        if window.exec_() == QDialog.Accepted:
            self.read_settings()

    def open_ingot_dialog(self):
        """Добавление нового слитка вручную"""
        window = IngotAddingDialog(self)
        if window.exec_() == QDialog.Accepted:
            pass

    def open_order_dialog(self):
        """Добавление нового заказа"""
        window = OrderAddingDialog(self)
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
        window.set_settings(settings)
        window.recordSavedSuccess.connect(self.confirm_order_adding)
        window.predictedIngotSaved.connect(self.save_tree)
        window.exec_()

    def read_settings(self):
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

    def write_settings(self):
        """Запись настроек в файл"""
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

    def save_tree(self, order: Dict, ingot: Dict, tree: Tree = None):
        """Сохранение корневого узла дерева"""
        file_name = self.get_file_name(order, ingot)
        path = 'schemes'
        abs_path = get_abs_path(file_name, path)
        with abs_path.open(mode='wb') as f:
            if tree:
                pickle.dump(tree, f)
            else:
                pickle.dump(self.tree, f)

    def is_file_exist(self, order: Dict, ingot: Dict):
        file_name = self.get_file_name(order, ingot)
        path = 'schemes'
        abs_path = get_abs_path(file_name, path)
        return abs_path.exists()

    def load_tree(self, order: Dict, ingot: Dict):
        """Загрузка корневого узла дерева из файла"""
        file_name = self.get_file_name(order, ingot)
        path = 'schemes'
        abs_path = get_abs_path(file_name, path)
        with abs_path.open(mode='rb') as f:
            self.tree = pickle.load(f)

    def get_file_name(self, order: Dict, ingot: Dict) -> str:
        """Создание имени файла для сохранения дерева раскроя"""
        extension = 'oci'
        return f"{order['order_id']}_{ingot['ingot_id']}_{order['creation_date']}.{extension}"


def get_abs_path(file_name, path=None) -> Path:
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

    window = OCIMainWindow()
    window.show()

    exit_code = application.exec_()

    total_time = time.time() - start
    print(f'{start = }, {total_time = }')
    logging.info(
        'Выход из приложения OCI. Время работы: %(time).2f мин.',
        {'time': total_time / 60}
    )

    sys.exit(exit_code)
