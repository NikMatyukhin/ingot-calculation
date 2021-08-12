"""Модуль главного окна"""


import copy
from operator import itemgetter
import sys
import pickle
import logging
import time
import math
from typing import Any, Dict, Optional, Sequence, Union, List, Tuple
from itertools import chain
from functools import partial
from contextlib import suppress
from collections import Counter, deque, namedtuple
from pathlib import Path

from PyQt5.QtCore import (
    Qt, QSettings, QModelIndex
)
from PyQt5.QtWidgets import (
    QApplication, QGraphicsDropShadowEffect, QGraphicsView, QMainWindow, QTableWidget, QTableWidgetItem,
    QMessageBox, QDialog, QVBoxLayout, QGraphicsScene, QLayout, QProgressDialog
)
from PyQt5.QtGui import QGuiApplication

from gui import ui_mainwindow
from widgets import (
    IngotSectionDelegate, ListValuesDelegate, ExclusiveButton,
    OrderDelegate, ZoomGraphicsView
)
from models import (
    IngotModel, IngotResidualsModel, OrderInformationComplectsModel, OrderModel
)
from service import (
    Field, OrderDataService, StandardDataService, FieldCollection,
    CatalogDataService, IngotStatusDataService
)
from dialogs import (
    IngotAssignmentDialog, IngotReadinessDialog, OrderAddingDialog,
    FullScreenWindow, OrderCompletingDialog, OrderEditingDialog
)
from messagebox import message_box_error, message_box_info
from storage import Storage
from charts.plan import CuttingPlanPainter
from charts.map import CuttingMapPainter
from catalog import Catalog
from settings import SettingsDialog
from exceptions import ForcedTermination
from log import setup_logging, timeit, log_operation_info

from sequential_mh.bpp_dsc.rectangle import (
    BinType, Direction, Material, Blank, Kit, Bin, Rectangle3d
)
from sequential_mh.bpp_dsc.tree import (
    BinNode, CuttingChartNode, Tree, solution_efficiency, is_defective_tree, is_cc_node,
    get_all_residuals, get_residuals
)
from sequential_mh.bpp_dsc.exception import BPPError
from sequential_mh.bpp_dsc.support import dfs
from sequential_mh.bpp_dsc.choice import choose_tree
from sequential_mh.bpp_dsc.stm import (
    _pack, _create_insert_template, predicate, is_empty_tree, is_empty_node
)
from sequential_mh.tsh.rect import RectangleType


Number = Union[int, float]
Sizes = Tuple[Number, Number, Number]
ListSizes = List[Sizes]


class OCIMainWindow(QMainWindow):
    """Главное окно"""
    
    def __init__(self):
        super(OCIMainWindow, self).__init__()
        self.ui = ui_mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)

        # Дерево раскроя текущего слитка
        self._tree: Tree = None
        # Подменяемое дерево раскроя из модели слитков-поддеревьев
        self._map_tree: Tree = None
        self.fusions_list = CatalogDataService.fusions_list()
        self.statuses_list = CatalogDataService.statuses_list()
        self.directions_list = CatalogDataService.directions_list()

        # Работа с настройками приложения: подгрузка настроек
        self.settings = QSettings('configs', QSettings.Format.IniFormat, self)

        self.cut_allowance = 2             # Припуск на разрез
        self.end_face_loss = 1             # Потери при обработке торцов (%)
        self.minimum_plate_width = 50      # Минимальная ширина пластины
        self.minimum_plate_length = 100    # Минимальная длина пластины
        self.rough_roll_edge_loss = 4      # Потери при обработке кромки до 3мм
        self.clean_roll_edge_loss = 2      # Потери при обработке кромки на 3мм
        self.guillotine_width = 1200       # Ширина ножа гильотины
        self.maximum_plate_length = 1250   # Максимальная длина пластины
        self.rough_roll_plate_width = 280  # Ширина пластины проката до 3мм
        self.clean_roll_plate_width = 450  # Ширина пластины проката на 3мм
        self.clean_roll_height = 3          # Толщина чистового проката
        self.admissible_deformation = 70   # Допустимая деформация проката (%)
        self.cutting_thickness = 4.2       # Толщина начала разрезов
        self.size_error = 2.0              # Погрешность ковки слитка
        self.allowance = 1.5               # Припуск на фрезировку слитка
        self.ingot_min_length = 70
        self.ingot_min_width = 70
        self.ingot_min_height = 20.0
        self.ingot_max_length = 180
        self.ingot_max_width = 180
        self.ingot_max_height = 30.0
        self.read_settings()

        # Установка визуальных дополнений приложения
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setColor(Qt.GlobalColor.black)
        self.shadow_effect.setYOffset(-5)
        self.shadow_effect.setXOffset(0)
        self.shadow_effect.setBlurRadius(20)
        self.ui.top_area.setGraphicsEffect(self.shadow_effect)
        
        self.shadow_effect_2 = QGraphicsDropShadowEffect()
        self.shadow_effect_2.setColor(Qt.GlobalColor.black)
        self.shadow_effect_2.setYOffset(-5)
        self.shadow_effect_2.setXOffset(0)
        self.shadow_effect_2.setBlurRadius(20)
        self.ui.order_name.setGraphicsEffect(self.shadow_effect_2)

        # Модель и делегат заказов
        self.order_model = OrderModel(Field('status_id', 1), self)
        self.order_delegate = OrderDelegate(self.ui.orders_view)
        self.ui.orders_view.setModel(self.order_model)
        self.ui.orders_view.setItemDelegate(self.order_delegate)

        # Модель слитков (обновляется при изменении текущего заказа)
        self.ingot_model = IngotModel('unused')
        # Делегат с закрываемыми и нумеруемыми слитками - для обычных заказов
        self.closed_ingot_dgt = IngotSectionDelegate(
            show_close = True, numerable = True, parent = self.ui.ingots_view)
        # Делегат с незакрываемыми слитками - для завершённых заказов
        self.unclosed_ingot_dgt = IngotSectionDelegate(
            show_close = False, numerable = True, parent = self.ui.ingots_view)
        self.ui.ingots_view.setModel(self.ingot_model)
        self.ui.ingots_view.setItemDelegate(self.closed_ingot_dgt)

        # Модель со слитками и их поддеревьями для карт раскроя
        self.residual_headers = [
            'Название', 'Партия', 'Сплав', 'Размеры', 'Эффективность', 'PATH'
        ]
        self.ingots_residuals_model = IngotResidualsModel(
            self.residual_headers, self)
        self.ui.ingots_residuals_view.setModel(self.ingots_residuals_model)
        for column, width in enumerate([115, 70, 80, 75, 10, 100]):
            self.ui.ingots_residuals_view.setColumnWidth(column, width)
        self.ui.ingots_residuals_view.setColumnHidden(5, True)

        # Модель комплектов (обновляется при изменении текущего заказа)
        self.complect_headers = [
            'Название', 'ID', 'Статус', 'Сплав', 'Длина', 'Ширина', 'Толщина',
            'Количество', 'Упаковано', 'Приоритет', 'Направление проката'
        ]
        self.complect_model = OrderInformationComplectsModel(
            self.complect_headers, self)
        # Делегаты для значений по ID в словарных таблицах
        self.status_dgt = ListValuesDelegate(self.statuses_list)
        self.fusion_dgt = ListValuesDelegate(self.fusions_list)
        self.direction_dgt = ListValuesDelegate(self.directions_list)
        self.ui.complects_view.setModel(self.complect_model)
        self.ui.complects_view.setItemDelegateForColumn(2, self.status_dgt)
        self.ui.complects_view.setItemDelegateForColumn(3, self.fusion_dgt)
        self.ui.complects_view.setItemDelegateForColumn(10, self.direction_dgt)
        for column in range(self.complect_model.columnCount()):
            self.ui.complects_view.resizeColumnToContents(column)

        # Сцены для отрисовки
        self.map_scene = QGraphicsScene()
        self.plan_scene = QGraphicsScene()

        # Создание специального представления для планов раскроя (zoom-view)
        self.plan_view = ZoomGraphicsView()
        self.plan_view.setAlignment(Qt.AlignCenter)
        self.plan_view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.ui.chart_area.layout().addWidget(self.plan_view)

        # Создание двух отрисовщиков для карт и планов иерархического дерева
        # слитков и подслитков
        self.plan_painter = CuttingPlanPainter(self.plan_scene)
        self.map_painter = CuttingMapPainter(self.map_scene)

        # Сигнал возврата на исходную страницу с информацией о заказах
        self.ui.information.clicked.connect(
            lambda: (
                self.ui.main_area.setCurrentIndex(0),
                self.ui.chart.setHidden(True),
                self.ui.information.setChecked(True),
            )
        )
        self.ui.plan.clicked.connect(
            lambda: (
                self.ui.main_area.setCurrentIndex(1),
                self.ui.chart.setHidden(False),
                self.ui.chart.setChecked(True),
            )
        )
        # Перерасчёт выбранного слитка
        self.ui.recalculate.clicked.connect(self.create_all_tree)

        # Показ текущего заказа по выбору
        self.ui.orders_view.clicked.connect(self.refresh_orders_view)
        
        # Смена дерева раскроя при выборе другого слитка или поддерева
        self.ui.ingots_residuals_view.clicked.connect(self.residual_changed)

        # Делегат заказа - события удаления или изменения заказа
        self.order_delegate.deleteIndexClicked.connect(self.order_removed)
        self.order_delegate.editIndexClicked.connect(self.open_edit_dialog)

        # Смена статуса кнопки расчёта в зависимости от статуса слитка
        self.ui.ingots_view.clicked.connect(self.ingot_changed)
        
        # Делегат слитка - события закрытия и готовности слитка
        self.closed_ingot_dgt.orderedIndexClicked.connect(self.ingot_ordered)
        self.closed_ingot_dgt.deliveredIndexClicked.connect(self.ingot_delivered)
        self.closed_ingot_dgt.deleteFromOrderClicked.connect(self.ingot_removed)
        
        # Сигналы кнопок на главном окне - другие секции или кнопки заказа
        self.ui.new_order.clicked.connect(self.open_order_dialog)
        self.ui.catalog.clicked.connect(self.open_catalog_window)
        self.ui.settings.clicked.connect(self.open_settings_dialog)
        self.ui.storage.clicked.connect(self.open_storage_window)
        self.ui.assign_ingot.clicked.connect(self.open_assign_dialog)
        self.ui.complete_order.clicked.connect(self.open_complete_dialog)

    @property
    def tree(self):
        return self._tree.root

    def refresh_orders_view(self, index: QModelIndex) -> None:
        """Переключатель активных заказов и открытых секций.

        Отвечает за то, чтобы одновременно была раскрыта только одна секция
        из списка заказов. Подгружает новую страницу заказа при его выборе.
        """
        if not index.isValid():
            return
        
        order = index.data(Qt.DisplayRole)
        if order['status_id'] in [3, 5]:
            # Если выбранный заказ уже завершён, то слитки закрыть нельзя,
            # и любой слиток пересчитать нельзя
            self.ui.ingots_view.setItemDelegate(self.unclosed_ingot_dgt)
        else:
            # Если заказ запланирован, в работе или ожидании, то можно всё
            self.ui.ingots_view.setItemDelegate(self.closed_ingot_dgt)
        self.ui.recalculate.setHidden(order['status_id'] in [3, 5])
        self.ui.assign_ingot.setHidden(order['status_id'] in [3, 5])
        self.ui.complete_order.setHidden(order['status_id'] in [3, 5])

        self.refresh_ingots_view(order)
        self.refresh_residuals_view(order)
        self.refresh_complects_view(order)

        self.ui.order_name.setText('Заказ ' + order['name'])
        self.ui.orders_information_area.setCurrentWidget(
            self.ui.information_page)

    def refresh_ingots_view(self, order: Dict):
        # Обновляем модель слитков по выбранному заказу, отмечаем первый слиток
        self.ingot_model.order = order['id']
        if self.ingot_model.rowCount():
            self.ui.ingots_view.setCurrentIndex(
                self.ingot_model.index(0, 0, QModelIndex()))
            self.ingot_changed(self.ui.ingots_view.currentIndex())
            self.ui.plan.setEnabled(self.scheme_count(order) != 0)
            self.ui.complete_order.setEnabled(self.scheme_count(order) != 0)
        else:
            self.ui.plan.setEnabled(False)
            self.ui.recalculate.setEnabled(False)
            self.ui.complete_order.setEnabled(False)
        
    def ingot_changed(self, current: QModelIndex) -> None:
        if not current.isValid():
            return
        
        ingot = current.data(Qt.DisplayRole)
        self.ui.recalculate.setEnabled(ingot['status_id'] not in [3, 5])

    def refresh_residuals_view(self, order: Dict):
        self.ingots_residuals_model.order = order['id']
        if self.ingots_residuals_model.rowCount():
            self.ui.ingots_residuals_view.expandAll()
            self.ui.ingots_residuals_view.setCurrentIndex(
                self.ingots_residuals_model.index(0, 0, QModelIndex()))
            self.ui.ingots_residuals_view.clicked.emit(
                self.ingots_residuals_model.index(0, 0, QModelIndex()))

    def residual_changed(self, index: QModelIndex):
        parent = self.ingots_residuals_model.parent(index)
        tree_index = self.ingots_residuals_model.index(index.row(), 5, parent)
        eff_index = self.ingots_residuals_model.index(index.row(), 4, parent)
        
        # Здесь получается дерево, по которому будет отображен раскрой планов
        # и карты одновременно
        self._map_tree = self.ingots_residuals_model.data(tree_index, Qt.DisplayRole)
        efficiency = self.ingots_residuals_model.data(eff_index, Qt.DisplayRole)
        self.update_height_line(self._map_tree)
        self.draw_map(self._map_tree, efficiency)
        self.go_to_map_page()

    def refresh_complects_view(self, order: Dict):
        self.complect_model.order = order['id']
        for column, width in enumerate([240, 90, 115, 90, 55, 65, 70, 85, 75]):
            self.ui.complects_view.setColumnWidth(column, width)
        self.ui.complects_view.setColumnHidden(1, True)
        self.ui.complects_view.expandAll()

    def ingot_ordered(self, index: QModelIndex) -> None:
        ingot = index.data(Qt.ItemDataRole.DisplayRole)
        size = 'x'.join(map(str, ingot['size']))
        _, fusion, density = StandardDataService.get_by_id(
            'fusions', Field('id', ingot['fusion_id'])
        )
        mass = str(round(math.prod(ingot['size'], start=density), 2))
        text = f'Размер: {size}\nСплав: {fusion}\nВес: {mass} г.'
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)

        message = str('Для заказа слитка отправьте мастеру участка получения '
                      'сплавов размеры и вес необходимого слитка.\n\n')
        clipboard_alert = str('\n\nПараметры скопированы в буфер обмена.')
        QMessageBox.information(
            self, 'Заказ слитка', message + text + clipboard_alert)
        
        success = StandardDataService.update_record('ingots', Field('id', ingot['id']), status_id=5)
        self.ingot_model.setData(index, {'status_id': 5}, Qt.EditRole)

    def ingot_delivered(self, index: QModelIndex) -> None:
        """Подтверждение готовности слитка.

        :param index: Индекс подтверждаемого слитка
        :type index: QModelIndex
        """
        ingot = self.ingot_model.data(index, Qt.DisplayRole)
        _, fusion, _ = StandardDataService.get_by_id(
            'fusions', Field('id', ingot['fusion_id']))
        # Запрос данных о готовности слитка
        window = IngotReadinessDialog(ingot['id'], ingot['size'], fusion, self)
        if window.exec_() == QDialog.Accepted:
            # Заказ возможно стоит сделать обычным и готовым
            order = self.ui.orders_view.currentIndex().data(Qt.DisplayRole)
            data = {'status_id': 1, 'batch': window.get_batch()}
            self.ingot_model.setData(index, data, Qt.EditRole)
            self.possible_change_status()
            self.refresh_residuals_view(order)

    def possible_change_status(self) -> None:
        """Проверка текущего заказа с возможным изменением статуса"""
        order_index = self.ui.orders_view.currentIndex()
        order = order_index.data(Qt.DisplayRole)
        # При обновлении статусов слитков нужно обновлять и модель 
        # слитков-поддеревьев на планах раскроя
        self.ingots_residuals_model.order = order['id']
        if self.ingot_model.rowCount():
            for row in range(self.ingot_model.rowCount()):
                ingot_index = self.ingot_model.index(row, 0, QModelIndex())
                ingot = self.ingot_model.data(ingot_index, Qt.DisplayRole)
                # Если есть запланированный слиток, то и заказ остаётся таким
                if ingot['status_id'] in [3, 5]:
                    break
            else:
                # Если запланированных слитков нет и заказ готов к началу
                self.change_status(order_index, 1)
        else:
            # Если слитков вообще нет, то заказ ожидает
            self.change_status(order_index, 0)

    def change_status(self, index: QModelIndex(), status: int) -> None:
        """Метод для обновления статуса заказа"""
        order = index.data(Qt.DisplayRole)
        self.order_model.setData(index, {'status_id': status}, Qt.EditRole)
        StandardDataService.update_record(
            'orders', Field('id', order['id']), status_id=status)
    
    def change_efficiency(self, index: QModelIndex(),
                          efficiency: float = None) -> None:
        """Метод для обновления эффективности заказа"""
        order = index.data(Qt.DisplayRole)
        if not efficiency:
            efficiency = OrderDataService.efficiency(
                Field('order_id', order['id']))
        self.order_model.setData(index, {'efficiency': efficiency}, Qt.EditRole)
        StandardDataService.update_record(
            'orders', Field('id', order['id']), efficiency=efficiency)

    def ingot_removed(self, index: QModelIndex) -> None:
        ingot = self.ingot_model.data(index, Qt.DisplayRole)
        order_index = self.ui.orders_view.currentIndex()
        order = order_index.data(Qt.DisplayRole)

        # FIXME: вариант в одну строку им не нравится, так как у кнопок текст   
        #        не "Да" + "Отмена", а "Ok" + "Cancel"
        # FIXME: если можно короче, сделаю короче, пока хз
        # TODO:  или можно вынести создание таких вопросительных окон в
        #        отдельный модуль, как было с информационными окнами
        message = QMessageBox(self)
        message.setWindowTitle('Подтверждение удаления')
        message.setText('Вы уверены, что хотите удалить этот слиток?')
        message.setIcon(QMessageBox.Icon.Question)
        answer = message.addButton('Да', QMessageBox.ButtonRole.AcceptRole)
        message.addButton('Отмена', QMessageBox.ButtonRole.RejectRole)
        message.exec()

        if answer == message.clickedButton():
            if ingot['status_id'] in [3, 5]:
                # Если слиток только в планах, то просто удаляем его
                success = StandardDataService.delete_by_id('ingots', Field('id', ingot['id']))
            elif ingot['status_id'] in [1, 2]:
                # Если слиток складской, то просто отвязываем от заказа
                success = StandardDataService.update_record('ingots', Field('id', ingot['id']), order_id=None)
            if not success:
                QMessageBox.critical(self, 'Ошибка удаления', 'Не удалось удалить слиток.', QMessageBox.Ok)
                return
            # Сначала нужно удалить карту раскроя от удаляемого слитка в
            # выбранном заказе и удалить его из модели слитков заказа...
            not_cutted_ingot = self.is_file_exist(order, ingot)
            if not_cutted_ingot:
                # self.load_tree(order, ingot)
                self.delete_tree(order, ingot=ingot)
            self.ingot_model.deleteRow(index.row())
            if not_cutted_ingot:
                # Необходимо сбросить статусы комплектов от этого слитка
                self.complect_model.discard_statuses(
                    order['id'], ingot['fusion_id'])
                # self.update_complect_statuses(
                #     order['id'], ingot['fusion_id'], discard=True)
                # Обновляем эффективность заказа
                self.change_efficiency(order_index)
            # Проверяем возможность изменения статуса заказа
            self.possible_change_status()
            # Обновляем итоговый вид заказа
            self.refresh_orders_view(order_index)

    def order_edited(self, data: Dict) -> None:
        index = self.ui.orders_view.currentIndex()
        self.order_model.setData(index, data, Qt.EditRole)
        self.possible_change_status()
        self.change_efficiency(index)
        self.refresh_orders_view(index)

    def order_removed(self, index: QModelIndex) -> None:
        order = index.data(Qt.DisplayRole)

        # FIXME: вариант в одну строку им не нравится, так как у кнопок текст
        #        не "Да" + "Отмена", а "Ok" + "Cancel"
        # FIXME: если можно короче, сделаю короче, пока хз
        # TODO:  или можно вынести создание таких вопросительных окон в
        #        отдельный модуль, как было с информационными окнами
        message = QMessageBox(self)
        message.setWindowTitle('Подтверждение удаления')
        message.setText(f'Вы точно хотите удалить заказ "{order["name"]}"?')
        message.setIcon(QMessageBox.Icon.Question)
        answer = message.addButton('Да', QMessageBox.ButtonRole.AcceptRole)
        message.addButton('Отмена', QMessageBox.ButtonRole.RejectRole)
        message.exec()

        if answer == message.clickedButton():
            for row in range(self.ingot_model.rowCount()):
                ingot_index = self.ingot_model.index(row, 0, QModelIndex())
                ingot = ingot_index.data(Qt.DisplayRole)
                if order['status_id'] != 3 and ingot['status_id'] in [1, 2]:
                    # Если слиток складской в незавершённом заказе, то нужно
                    # отвязать слиток
                    StandardDataService.update_record('ingots', Field('id', ingot['id']), order_id=None)
                else:
                    # Если слиток любой, а заказ завершён, то просто удаляем
                    StandardDataService.delete_by_id('ingots', Field('id', ingot['id']))
            success = StandardDataService.delete_by_id('orders', Field('id', order['id']))
            if not success:
                QMessageBox.critical(self, 'Ошибка удаления', 'Не удалось удалить заказ.', QMessageBox.Ok)
                return
            # Если удаление прошло успешно, то можно удалять все схемы этого
            # заказа и удалять его из модели
            self.delete_tree(order)
            self.order_model.deleteRow(index.row())
            self.ui.orders_information_area.setCurrentWidget(self.ui.default_page)
            self.ui.orders_view.clearSelection()

    def update_complect_statuses(self, order_id: int, ingot_fusion: int,
                                 discard: bool = False) -> None:
        """Обновление статусов заготовок"""
        # Переходим по всем изделиям в заказе
        model = self.complect_model
        complect_counter = dict()
        for row in range(model.rowCount(QModelIndex())):
            article = model.index(row, 0, QModelIndex())
            article_name = model.data(article, Qt.DisplayRole)

            # Переходим по всем заготовкам в изделии
            for sub_row in range(model.rowCount(article)):
                detail_fusion = int(model.data(model.index(sub_row, 3, article), Qt.DisplayRole))

                # Если не совпадают сплав заготовки и выбранного слитка - пропускаем
                if detail_fusion != ingot_fusion:
                    continue

                # Собираем все нужные данные по колонкам
                name = model.data(model.index(sub_row, 0, article), Qt.DisplayRole)
                depth = float(model.data(model.index(sub_row, 6, article), Qt.DisplayRole))
                complect_counter[str(depth) + '_' + article_name + '_' + name] = {
                    'detail_id': int(model.data(model.index(sub_row, 1, article), Qt.DisplayRole)),
                    'depth': depth,
                    'amount': int(model.data(model.index(sub_row, 7, article), Qt.DisplayRole)),
                    'status_id': model.index(sub_row, 2, article),
                    'total': model.index(sub_row, 8, article)
                }

        updates = FieldCollection(['status_id', 'total', 'order_id', 'detail_id'])
        order = Field('order_id', order_id)

        # Если режим сброса, то просто находим все упакованные заготовки
        if discard and self.tree:
            placed_counter = Counter()
            for leave in self.tree.cc_leaves:
                placed_counter += Counter(b.name for b in leave.placed)
            for name in placed_counter:
                if name not in complect_counter:
                    continue
                detail = Field('detail_id', complect_counter[name]['detail_id'])
                updates.append(Field('status_id', 0), Field('total', 0), order, detail)
                model.setData(complect_counter[name]['status_id'], 0, Qt.EditRole)
                model.setData(complect_counter[name]['total'], 0, Qt.EditRole)
            OrderDataService.update_statuses(updates)
            return

        # Подсчитываем количество неразмещенных заготовок (название: количество)
        unplaced_counter = Counter(b.name for b in self._tree.main_kit)
        for leave in self.tree.cc_leaves:
            unplaced_counter -= Counter(b.name for b in leave.placed)

        # Сначала проходимся по счётчику неразмещённых заготовок
        for name in unplaced_counter:
            detail = Field('detail_id', complect_counter[name]['detail_id'])

            # Если количество заготовок совпадает с остатком
            if complect_counter[name]['amount'] == unplaced_counter[name]:
                continue
                # updates.append(Field('status_id', 4), Field('total', 0), order, detail)
                # model.setData(complect_counter[name]['status_id'], 4, Qt.EditRole)
                # model.setData(complect_counter[name]['total'], 0, Qt.EditRole)
            # Если количество заготовок не совпадает с остатком
            else:
                updates.append(
                    Field('status_id', 5),
                    Field(
                        'total',
                        complect_counter[name]['amount'] - unplaced_counter[name]
                    ),
                    order, detail
                )
                model.setData(complect_counter[name]['status_id'], 5, Qt.EditRole)
                model.setData(
                    complect_counter[name]['total'],
                    complect_counter[name]['amount'] - unplaced_counter[name],
                    Qt.EditRole
                )

        # В конце проходимся по всем заготовкам чтобы найти пропущенные толщины
        for name in complect_counter:
            detail = Field('detail_id', complect_counter[name]['detail_id'])

            # if complect_counter[name]['depth'] not in self.steps():
            #     updates.append(Field('status_id', 4), Field('total', 0), order, detail)
            #     model.setData(complect_counter[name]['status_id'], 4, Qt.EditRole)
            #     model.setData(complect_counter[name]['total'], 0, Qt.EditRole)
            # Если количество неразмещённых заготовок равно нулю
            if name not in unplaced_counter:
                updates.append(Field('status_id', 1), Field('total', complect_counter[name]['amount']), order, detail)
                model.setData(complect_counter[name]['status_id'], 1, Qt.EditRole)
                model.setData(complect_counter[name]['total'], complect_counter[name]['amount'], Qt.EditRole)
        OrderDataService.update_statuses(updates)

    def create_all_tree(self) -> None:
        order_index = self.ui.orders_view.currentIndex()
        order = order_index.data(Qt.DisplayRole)
        model = self.ui.ingots_view.model()

        all_blanks = self.get_all_blanks()
        placed_blanks: Dict[str, Counter] = {}
        ingots = []
        for ingot_index in range(model.rowCount()):
            ingot_idx_model = model.index(ingot_index, 0)
            ingot_data = ingot_idx_model.data()
            fusion = StandardDataService.get_by_id('fusions', Field('id', ingot_data['fusion_id']))
            material = Material(fusion[1], fusion[2], 1.)

            # фильтрация зеленых слитков и запоминание размещенных элементов
            if ingot_data['status_id'] == 3:
                if material.name not in placed_blanks:
                    placed_blanks[material.name] = Counter()

                self.load_tree(order, ingot_data)

                for leave in self.tree.cc_leaves:
                    placed_blanks[material.name] += Counter(b.name for b in leave.placed)
            else:
                ingots.append((ingot_idx_model, ingot_data, material))

        # сортируем по объему в порядке неубывания
        ingots.sort(key=lambda item: math.prod(item[1]['size']))

        for index, ingot, material in ingots:
            if material.name not in placed_blanks:
                placed_blanks[material.name] = Counter()

            kit = self.create_details_kit(
                all_blanks[material.name], material, placed_blanks[material.name]
            )
            if kit.is_empty():
                break

            ef_res = self.create_tree(
                order, ingot, material, kit
            )
            if ef_res:
                for leave in self._tree.root.cc_leaves:
                    placed_blanks[material.name] += Counter(
                        b.name for b in leave.placed)

                # Если раскрой дерева для слитка успешен, то обовляем его
                self.ingot_model.setData(
                    index, {'efficiency': ef_res}, Qt.EditRole
                )
                StandardDataService.update_record(
                    'ingots', Field('id', ingot['id']), efficiency=ef_res
                )
                # Также необходимо сохранить дерево этого слитка и обновить
                # модель с комплектами и их статусами
                self.update_complect_statuses(order['id'], ingot['fusion_id'])
                self.save_tree(order, ingot)
                self.possible_change_status()
        self.change_efficiency(order_index)
        self.refresh_orders_view(order_index)

    def create_tree(self, order: Dict, ingot: Dict, material: Material,
                    kit: Kit) -> Optional[Tuple[float, float]]:
        # Отображение прогресса раскроя
        progress = QProgressDialog('OCI', 'Закрыть', 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle('Раскрой')
        progress.forceShow()
        order_name = order['name']
        size = ingot['size']
        _id = int(order['id'])
        log_operation_info(
            'create_cut', {'name': order_name, 'alloy': material.name},
            identifier=_id
        )
        progress.setLabelText('Процесс раскроя...')
        try:
            log_operation_info(
                'cut_info',
                {
                    'name': order_name, 'alloy': material.name,
                    'size': 'x'.join(map(str, size)),
                    'blanks': kit.qty(), 'heights': len(kit.keys())
                }, identifier=_id
            )
            efficiency = self.create_cut(size, kit, material, progress=progress)
        except ForcedTermination:
            log_operation_info(
                'user_inter_cut', {'name': order_name, 'alloy': material.name},
                identifier=_id
            )
            message_box_info('Процесс раскроя был прерван!', self)
            return
        except BPPError as ex:
            message_box_error(str(ex), parent=self)
            return
        except Exception as exception:
            QMessageBox.critical(
                self, 'Раскрой завершился с неизвестной ошибкой', f'{exception}', QMessageBox.Ok
            )
            return
        else:
            progress.setLabelText('Завершение раскроя...')
            progress.close()
            return round(efficiency, 2)

    def get_all_blanks(self) -> Dict:
        """Получение всех заготовок из заказа

        :return: Набор заготовок сгруппированных по сплаву в виде словаря
        :rtype: Dict[str, list]
        """
        Detail = namedtuple(
            'Detail',
            ('length', 'width', 'height', 'priority', 'direction', 'name', 'amount')
        )
        model = self.complect_model
        details: Dict[str, List[Detail]] = {}
        # Переходим по всем изделиям в заказе
        for row in range(model.rowCount(QModelIndex())):
            parent = model.index(row, 0, QModelIndex())
            parent_name = model.data(parent, Qt.DisplayRole)

            # Переходим по всем заготовкам в изделии
            for sub_row in range(model.rowCount(parent)):
                fusion_id: int = model.data(model.index(sub_row, 3, parent), Qt.DisplayRole)
                detail_fusion: str = StandardDataService.get_by_id('fusions', Field('id', fusion_id))[1]

                # Собираем все нужные данные по колонкам
                name: str = model.data(model.index(sub_row, 0, parent), Qt.DisplayRole)
                direction_id = int(model.data(model.index(sub_row, 10, parent), Qt.DisplayRole))
                direction_code = 3 if direction_id == 0 else 2
                direction = Direction(direction_code)

                detail=Detail(
                    length=int(model.data(model.index(sub_row, 4, parent), Qt.DisplayRole)),
                    width=int(model.data(model.index(sub_row, 5, parent), Qt.DisplayRole)),
                    height=float(model.data(model.index(sub_row, 6, parent), Qt.DisplayRole)),
                    priority = int(model.data(model.index(sub_row, 9, parent), Qt.DisplayRole)),
                    direction=direction,
                    name = parent_name + '_' + name,
                    amount=int(model.data(model.index(sub_row, 7, parent), Qt.DisplayRole))
                )
                if detail_fusion not in details:
                    details[detail_fusion] = []
                details[detail_fusion].append(detail)
        return details

    @staticmethod
    def create_details_kit(blanks, material: Material, exclude=None) -> Kit:
        """Создание набора заготовок

        :param blanks: Набор заготовок в виде списка кортежей.
                        Кортежи должны иметь формат:
                        (length, width, height, priority, direction, name, amount)
        :type blanks: list[tuple]
        :param material: Материал
        :type material: Material
        :param exclude: Набор заготовок, которые нужно исключить.
                        Формат: {имя_заготовки: количество}, defaults to None
        :type exclude: dict, optional
        :return: Набор заготовок
        :rtype: Kit
        """
        kit_: List[Blank] = []
        if exclude is None:
            exclude = {}
        for detail in blanks:
            number = detail[-1]
            for _ in range(number - exclude.get(detail[-2], 0)):
                blank = Blank(*detail[:4], direction=detail[4], material=material)
                blank.name = detail[-2]
                kit_.append(blank)
        kit: Kit = Kit(kit_)
        kit.sort('width')
        return kit

    def get_details_kit(self, material: Material) -> Kit:
        """Формирование набора заготовок

        :param material: Материал
        :type material: Material
        :return: Набор заготовок
        :rtype: Kit
        """
        # TODO: Удалить метод
        model = self.complect_model
        details = []
        # Переходим по всем изделиям в заказе
        for row in range(model.rowCount(QModelIndex())):
            parent = model.index(row, 0, QModelIndex())
            parent_name = model.data(parent, Qt.DisplayRole)

            # Переходим по всем заготовкам в изделии
            for sub_row in range(model.rowCount(parent)):
                fusion_id = model.data(model.index(sub_row, 3, parent), Qt.DisplayRole)
                detail_fusion = StandardDataService.get_by_id('fusions', Field('id', fusion_id))[1]

                # Если не совпадают сплав заготовки и выбранного слитка - пропускаем
                if detail_fusion != material.name:
                    continue

                # Собираем все нужные данные по колонкам
                name: str = model.data(model.index(sub_row, 0, parent), Qt.DisplayRole)
                length = int(model.data(model.index(sub_row, 4, parent), Qt.DisplayRole))
                width = int(model.data(model.index(sub_row, 5, parent), Qt.DisplayRole))
                depth = float(model.data(model.index(sub_row, 6, parent), Qt.DisplayRole))
                sizes: Sizes = (length, width, depth)
                amount = int(model.data(model.index(sub_row, 7, parent), Qt.DisplayRole))
                priority = int(model.data(model.index(sub_row, 9, parent), Qt.DisplayRole))
                direction_id = int(model.data(model.index(sub_row, 10, parent), Qt.DisplayRole))
                direction_code = 3 if direction_id == 0 else 2
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
                   progress: QProgressDialog = None) -> float:
        """Метод запуска алоритма раскроя.

        :param ingot_size: Размер слитка в формате (длина, ширина, толщина)
        :type ingot_size: tuple[Number, Number, Number]
        :param kit: Набор заготовок
        :type kit: Kit
        :param material: Материал
        :type material: Material
        """
        order = self.ui.orders_view.currentIndex().data(Qt.DisplayRole)
        settings = self.general_settings(order)
        ingot_bin = Bin(*ingot_size, material=material)
        tree = Tree(BinNode(ingot_bin, kit=kit))
        tree = self.stmh_idrd(tree, restrictions=settings, progress=progress)
        self._tree = tree

        # NOTE: своя визуализация для отладки
        # debug_graph_tree(tree)
        # for node in self.tree.cc_leaves:
        #     debug_visualize(node, 'Основной')
        #     if node.subtree:
        #         for subtree in node.subtree:
        #             for subnode in subtree.root.cc_leaves:
        #                 debug_visualize(subnode, f'Остаток от {node.bin.height} мм')

        efficiency = solution_efficiency(self.tree, list(dfs(self.tree)), tree.main_kit, is_total=True)

        # NOTE: тест перерасчета
        # node_1 = tree.node_by_id(55)
        # node_1 = tree.node_by_id(63)
        # print(f'{node_1.bin.size}')
        # node_2 = tree.node_by_id(64)
        # print(f'{node_2.bin.size}')
        # self.recalculation(tree, [(node_2, (30, 180, 4.2)), (node_1, (50, 180, 4.2))], settings)
        return efficiency

    @timeit
    def stmh_idrd(self, tree: Tree, with_filter: bool = True,
                  restrictions: dict = None, progress: QProgressDialog = None,
                  level_subtree: int = 0, with_priority: bool = True):
        is_main = True
        doubling = False
        start_step, steps = 0, 0
        if restrictions:
            cut_thickness = restrictions.get('cutting_thickness')
            if cut_thickness and cut_thickness >= max(tree.root.kit.keys()):
                doubling = True
            else:
                # cut_thickness = max(tree.root.kit.keys())
                restrictions['cutting_thickness'] = max(tree.root.kit.keys())
            # doubling = cut_thickness >= max(tree.root.kit.keys())
        if progress:
            steps = number_of_steps(len(tree.root.kit.keys()), doubling=doubling)
            # Костыль. Умножение на константу для учета одинаковых веток
            # print(f'Рассчитанное кол-во шагов: {steps}')
            steps = int(4 * steps)
            progress.setRange(0, steps)
        trees_vertical = self._stmh_idrd(
            tree, restrictions=restrictions, local=not is_main,
            with_filter=with_filter, progress=progress, end_progress=False,
            direction=1, steps=steps, level_subtree=level_subtree, with_priority=with_priority
        )
        if progress:
            start_step = progress.value()
        trees_horizontal = self._stmh_idrd(
            tree, restrictions=restrictions, local=not is_main,
            with_filter=with_filter, progress=progress, direction=2,
            start_step=start_step, steps=steps, level_subtree=level_subtree, with_priority=with_priority
        )
        trees = [*trees_vertical, *trees_horizontal]

        if restrictions:
            max_size = restrictions.get('max_size')
        else:
            max_size = None
        if progress:
            progress.setLabelText('Фильтрация решений...')
        if with_filter:
            trees = [
                item for item in trees if not is_defective_tree(item, max_size)
            ]

        if not trees and level_subtree == 0:
            raise BPPError(
                'Не удалось получить раскрой. Измените приоритеты или ограничения'
            )
        elif not trees:
            return

        print(f'Годных деревьев: {len(trees)}')
        # for t in trees:
        #     ef = solution_efficiency(
        #         t.root, list(dfs(t.root)), t.main_kit, nd=True, is_p=True
        #     )
        #     print(f'Узлов проката: {foo(t.root)}; эффективность: {ef:.6f}')
        if progress:
            progress.setLabelText('Выбор оптимального решения...')

        best, _ = choose_tree(trees)

        for node in best.root.cc_leaves:
            print(node.bin.height, node._id)
        get_all_residuals(best)
        return best

    def _stmh_idrd(self, tree: Tree, local: bool = False,
                   with_filter: bool = True, restrictions: dict = None,
                   progress: QProgressDialog = None, end_progress: bool = True,
                   direction: int = 1, start_step: int = 0, steps: int = 0,
                   level_subtree: int = 0, with_priority: bool = True) -> List[Tree]:
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
        step = start_step
        point_counter = 2

        if restrictions:
            max_size = restrictions.get('max_size')
        else:
            max_size = None

        while level:
            step += 1
            new_level: deque = deque([])
            for _, tree_ in enumerate(level):
                # Костыль для небольшого увеличения прогресса
                # в случае, когда он переполняется
                if step >= steps and progress:
                    steps = int(step * 1.1)
                    progress.setRange(0, steps)
                if with_filter and is_defective_tree(tree_, max_size=max_size):
                    # Додумать на сколько уменьшать
                    # min_height = min(map(lambda item: item.bin.height, tree_.root.cc_leaves))
                    # steps -= number_of_steps(len([x for x in tree.root.kit.keys() if x < min_height]), doubling=False)
                    # steps -= 1
                    # progress.setRange(0, steps)
                    # progress.setValue(step - 1)
                    continue
                if is_empty_tree(tree_):
                    result.append(tree_)
                else:
                    new_level.append(tree_)
            level = deque(new_level)
            if not level:
                break

            tree = level.popleft()
            nodes_: List[Any] = [
                node for node in tree.root.leaves() if not is_empty_node(node)
            ]
            nodes: deque = deque(sorted(nodes_, key=predicate))
            node = nodes[0]
            if is_cc_node(node):
                _pack(node, level, restrictions, with_priority=with_priority)
                # контролируем уровень построения поддеревьев
                # FIXME: раскоментировать для учета остатков
                if tree._type == 0:
                    level_subtree = 0
                if level_subtree < 1:
                    level_subtree += 1
                    self.create_subtree(node, restrictions, level_subtree)
                    level_subtree -= 1
                if is_empty_tree(tree):
                    result.append(tree)
                else:
                    level.append(tree)
            else:
                _create_insert_template(
                    node, level, tree, local, restrictions,
                    direction=direction
                )
            # print(f'{step = }; {len(level)}')
            if progress:
                progress.setValue(step)
                progress.setLabelText('Процесс раскроя.' + '.' * point_counter + ' ' * (2 - point_counter))
                point_counter = (point_counter + 1) % 3
                # print(f'{progress.wasCanceled() = }')
                if progress.wasCanceled():
                    raise ForcedTermination('Процесс раскроя был прерван')
        print(f'Кол-во шагов для {len(tree.root.kit.keys())} толщин: {step} ({steps})')
        # костыль для завершения прогресса
        if end_progress and step < steps and progress:
            progress.setValue(steps)

        return result

    def create_subtree(self, node: CuttingChartNode, restrictions: Dict,
                       level_subtree: int) -> None:
        """Создание поддерева для остатка

        :param node: Узел, содержащий остатки
        :type node: CuttingChartNode
        :param restrictions: Ограничения
        :type restrictions: dict
        :param level_subtree: Уровень поддерева, ограничивает
                              рекурсивное построение деревьев
        :type level_subtree: int
        """
        min_size = self.minimum_plate_length, self.minimum_plate_width
        tailings = get_residuals(node)
        tailings = filtration_residues(node.result.tailings, min_size=min_size)
        suitable_residues = [
            t for t in tailings
            if incoming_rectangles(t, node.bin.height, node.result.unplaced)
        ]
        # если нет прямоугольников для размещения текущей
        # толщины пробуем упаковать другие
        adjacent_branch = node.adjacent_branch()
        if adjacent_branch:
            adj_node = adjacent_branch.adj_leaves[0]
        else:
            return
        if not suitable_residues and not adj_node.kit.is_empty():
            # получить неупакованные элементы из соседней ветки
            # построить дерево для остатков
            for tailing in tailings:
                new_root = BinNode(
                    Bin(
                        tailing.length, tailing.width, node.bin.height,
                        material=node.bin.material
                    ),
                    copy.deepcopy(adj_node.kit)
                )
                new_tree = Tree(new_root)
                new_tree._type = 1
                try:
                    new_tree = self.stmh_idrd(
                        new_tree, restrictions=restrictions,
                        level_subtree=level_subtree, with_priority=False
                    )
                except BPPError:
                    print(f'\tОстаток {tailing.length, tailing.width, node.bin.height} из {node.bin}: {adj_node.kit.keys()}')
                else:
                    if new_tree is None:
                        continue
                    if new_tree.root.children:
                        tailing.rtype = RectangleType.USED_RESIDUAL
                        node.subtree.append(new_tree)
                    # как быть если есть приоритет? когда частичная упаковка текущей толщины
                    # получить упакованные элементы
                    # удалить упакованные элементы из соседней ветки
                    for subnode in new_tree.root.cc_leaves:
                        blanks = [r.rectangle for r in chain.from_iterable(subnode.result.blanks.values())]
                        adj_node.kit.delete_items(list(blanks), subnode.bin.height)
                if adj_node.kit.is_empty():
                    break

    @timeit
    def optimal_ingot_size(self, main_tree: Tree, min_size: Sizes,
                           max_size: Sizes, restrictions: Dict,
                           progress: QProgressDialog = None) -> Tree:
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

        doubling = False
        start_step, steps = 0, 0
        if restrictions:
            cut_thickness = restrictions.get('cutting_thickness')
            if cut_thickness and cut_thickness >= max(main_tree.root.kit.keys()):
                doubling = True
            else:
                restrictions['cutting_thickness'] = max(main_tree.root.kit.keys())
        if progress:
            steps = number_of_steps(len(main_tree.root.kit.keys()), doubling=doubling)
            # Костыль. Умножение на константу для учета одинаковых веток
            # print(f'Рассчитанное кол-во шагов: {steps}')
            steps = int(6 * steps)
            progress.setRange(0, steps)

        trees_vertical = self._stmh_idrd(
            main_tree, restrictions=restrictions, local=False,
            with_filter=False, progress=progress, end_progress=False,
            direction=1, steps=steps
        )
        if progress:
            start_step = progress.value()
        trees_horizontal = self._stmh_idrd(
            main_tree, restrictions=restrictions, local=False,
            with_filter=False, progress=progress, direction=2,
            start_step=start_step, steps=steps
        )
        trees = [*trees_vertical, *trees_horizontal]

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
        if not trees:
            raise BPPError('Не удалось получить раскрой')
        # best = max(
        #     trees,
        #     key=lambda item: solution_efficiency(
        #         item.root, list(dfs(item.root)), item.main_kit, nd=True, is_p=True
        #     )
        # )
        best, _ = choose_tree(trees)
        get_all_residuals(best)

        # NOTE: своя визуализация для отладки
        # debug_graph_tree(best)
        # for node in best.root.cc_leaves:
        #     debug_visualize(node, 'Основной')
        #     if node.subtree:
        #         for subtree in node.subtree:
        #             for subnode in subtree.root.cc_leaves:
        #                 debug_visualize(subnode, f'Остаток от {node.bin.height} мм')
        return best

    def recalculation(self, tree, updatable_nodes, restrictions):
        # tree - исходное дерево
        # nodes - список пар из узлов и новых размеров
        node = updatable_nodes[0][0]
        if len(updatable_nodes) == 2:
            main_kit = copy.deepcopy(node.parent.parent.kit)
        else:
            main_kit = copy.deepcopy(node.kit)
        for i, (node, new_size) in enumerate(updatable_nodes):
            ingot_bin = Bin(*new_size, material=node.bin.material)
            # создать новое дерево
            new_tree = Tree(BinNode(ingot_bin, kit=copy.deepcopy(main_kit)))
            new_tree = self.stmh_idrd(new_tree, restrictions=restrictions)
            # удалить размещенные заготовки
            # unplaced_counter = Counter(b.name for b in new_tree.main_kit)
            # for leave in new_tree.root.cc_leaves:
            #     unplaced_counter -= Counter(b.name for b in leave.placed)

            for cc_node in new_tree.root.cc_leaves:
                blanks = [r.rectangle for r in chain.from_iterable(cc_node.result.blanks.values())]
                main_kit.delete_items(list(blanks), cc_node.bin.height)

            # меняем поддерево
            parent = node.parent
            print(f'{node.bin.bin_type = }')
            print(f'{node.parent = }')

            new_tree.root.bin.bin_type = node.bin.bin_type
            new_tree.root.parent = parent
            # node.parent = None
            # parent.children = new_tree.root
            parent.delete(node)
            parent.add(new_tree.root)

            # NOTE: своя визуализация для отладки
            # debug_graph_tree(tree, name=f'tree_{i}')
            # for node in tree.root.cc_leaves:
            #     debug_visualize(node, 'Основной')
            #     if node.subtree:
            #         for subtree in node.subtree:
            #             for subnode in subtree.root.cc_leaves:
            #                 debug_visualize(subnode, f'Остаток от {node.bin.height} мм')


    def save_residuals(self, ingot: Dict, order: Dict) -> Sequence[Tuple]:
        """Сохранение остатков в БД"""
        batch = ingot['batch']
        min_size = self.minimum_plate_length, self.minimum_plate_width

        if self.is_file_exist(order, ingot):
            self.load_tree(order, ingot)
        if self.tree is None:
            raise ValueError('Дерево не рассчитано')

        all_tailings = []
        for adj_node in self.tree.adj_leaves:
            if is_suitable_sizes(adj_node.bin, min_size=min_size):
                all_tailings.append(
                    (adj_node.bin.length, adj_node.bin.width, adj_node.bin.height,
                    adj_node.bin.material, batch)
                )
        for node in self.tree.cc_leaves:
            tailings = [(tailing, node.bin.height) for tailing in node.result.tailings]
            for subtree in node.subtree:
                for subnode in subtree.root.cc_leaves:
                    tailings.extend([(tailing, subnode.bin.height) for tailing in subnode.result.tailings])
                tailings.extend([(adj_node.bin, adj_node.bin.height) for adj_node in subtree.root.adj_leaves])
            tailings = filtration_residues(tailings, min_size=min_size, key=itemgetter(0))
            for tailing, height in tailings:
                # получаем сплав
                all_tailings.append(
                    (tailing.length, tailing.width, height,
                     node.bin.material, batch)
                )
        return all_tailings

    def steps(self, tree: Tree) -> List[float]:
        """Список толщин"""
        leaves = tree.root.cc_leaves
        height_list = [leave.bin.height for leave in leaves]
        return height_list

    def create_heights_line(self, steps: List[float]) -> List[ExclusiveButton]:
        heights_line = [ExclusiveButton(name='Карта\nраскроя')]
        for i, height in enumerate(steps):
            name = f'{height} мм'
            if steps.count(height) > 1:
                name += f' ({steps[:i].count(height) + 1})'
            heights_line.append(ExclusiveButton(name=name, index=i))
        return heights_line

    def update_height_line(self, tree: Tree) -> None:
        """Подготовка страницы с планами раскроя"""
        self.clear_layout(self.ui.heigths_layout)
        heights_line = self.create_heights_line(self.steps(tree))

        for button in heights_line:
            button.clicked.connect(self.height_changed)
            self.ui.heigths_layout.addWidget(button)
        
        self.ui.heigths_layout.addStretch()
        heights_line[0].setChecked(True)

    def height_changed(self) -> None:
        """Просмотр другой толщины"""
        button = self.sender()
        
        # Сброс рисовальщика и обновление представления плана раскроя
        self.plan_painter.setup()
        self.plan_view.viewport().update()
        self.plan_view.verticalScrollBar().setValue(
            self.plan_view.verticalScrollBar().minimum()
        )
        # Если кнопка без значения index, то это кнопка карты раскроя
        if button.index is None:
            self.go_to_map_page()
        else:
            self.go_to_plan_page(button.index)

    def go_to_map_page(self) -> None:
        """Переход на страницу с исходным слитком"""
        self.plan_view.setScene(self.map_scene)

    def go_to_plan_page(self, index: int) -> None:
        """Переход на страницу с планом толщины"""
        self.plan_scene.clear()
        self.plan_view.setScene(self.plan_scene)

        node: CuttingChartNode = self._map_tree.root.cc_leaves[index]
        self.plan_painter.setBin(
            math.ceil(node.bin.length),
            math.ceil(node.bin.width),
            round(node.bin.height, 1)
        )
        for blank in node.result:
            rect = blank.rectangle
            self.plan_painter.addBlank(
                math.ceil(rect.length),
                math.ceil(rect.width),
                round(rect.height, 1),
                round(blank.x, 1),
                round(blank.y, 1),
                rect.name
            )
        self.plan_painter.drawPlan()

    def draw_map(self, tree: Tree, efficiency: float) -> None:
        self.map_scene.clear()
        self.plan_view.viewport().update()
        self.plan_view.verticalScrollBar().setValue(
            self.plan_view.verticalScrollBar().minimum()
        )
        self.plan_view.horizontalScrollBar().setValue(
            self.plan_view.horizontalScrollBar().minimum()
        )
        self.map_painter.setTree(tree)
        self.map_painter.setEfficiency(efficiency)
        self.map_painter.drawTree()

    def clear_layout(self, layout: QLayout) -> None:
        """Метод для очистки слоёв компоновки

        :param layout: Слой с которого удаляются виджеты по заданным правилам
        :type layout: QLayout
        """
        while item := layout.takeAt(0):
            if item.widget():
                item.widget().deleteLater()
            del item

    def open_fullscreen_window(self) -> None:
        """Просмотр карты в полноэкранном режиме"""
        window = FullScreenWindow(self)
        window.set_scene(self.map_scene)
        window.showMaximized()

    def open_catalog_window(self) -> None:
        """Работа со справочником изделий"""
        window = Catalog(self)
        window.show()

    def open_storage_window(self) -> None:
        """Работа с хранилищем (складом) слитков"""
        window = Storage(self)
        window.show()

    def open_settings_dialog(self) -> None:
        """Работа с окном настроек"""
        window = SettingsDialog(self, self.settings)
        if window.exec_() == QDialog.Accepted:
            self.read_settings()

    def open_assign_dialog(self) -> None:
        """Добавление слитка к заказу"""
        order_index = self.ui.orders_view.currentIndex()
        order = order_index.data(Qt.DisplayRole)
        
        window = IngotAssignmentDialog(
            order, self.general_settings(order), self.forge_settings(), self)
        window.predictedIngotSaved.connect(self.save_tree)

        if window.exec() == QDialog.DialogCode.Accepted:
            # Если был добавлен хотя бы один запланированный слиток, нужно
            # сделать заказ запланированным в любом случае
            if window.predicted and order['status_id'] != 2:
                self.change_status(order_index, 2)
            self.change_efficiency(order_index)
        self.refresh_orders_view(order_index)

    def open_order_dialog(self) -> None:
        """Добавление нового заказа"""
        window = OrderAddingDialog(self.cutting_thickness, self)
        window.recordSavedSuccess.connect(self.order_model.appendRow)
        window.exec_()

    def open_complete_dialog(self) -> None:
        """Заврешение выбранного заказа и добавление остатков"""
        residuals = []
        order_index = self.ui.orders_view.currentIndex()
        order = order_index.data(Qt.DisplayRole)
        if self.ingot_model.rowCount() == 0:
            message_box_info('В заказе отсутствует металл!', self)
            return
        for row in range(self.ingot_model.rowCount()):
            ingot = self.ingot_model.index(row, 0, QModelIndex()).data(Qt.DisplayRole)
            if ingot['status_id'] in [3, 5]:
                message_box_info('Добавьте расчетный слиток на склад!', self)
                return
            with suppress(TypeError):
                residuals.extend(self.save_residuals(ingot, order))
        window = OrderCompletingDialog(residuals, self)
        if window.exec() == QDialog.Accepted:
            self.change_status(order_index, 3)
            self.refresh_orders_view(order_index)

    def open_edit_dialog(self) -> None:
        """Изменение текущего заказа"""
        order = self.ui.orders_view.currentIndex().data(Qt.DisplayRole)
        if self.scheme_count(order):
            self.delete_tree(order)
            for row in range(self.ingot_model.rowCount()):
                ingot_index = self.ingot_model.index(row, 0, QModelIndex())
                ingot = ingot_index.data(Qt.DisplayRole)
                if ingot['status_id'] in [3, 5]:
                    # Если слиток только в планах, то просто удаляем его
                    StandardDataService.delete_by_id('ingots', Field('id', ingot['id']))
        window = OrderEditingDialog(order, self.complect_model, self)
        window.orderEditedSuccess.connect(self.order_edited)
        window.show()

    def read_settings(self) -> None:
        """Чтение настроек из файла"""
        self.cut_allowance = self.settings.value(
            'cutting/cut_allowance', defaultValue=2, type=int)
        self.end_face_loss = self.settings.value(
            'cutting/end_face', defaultValue=0.01, type=float)
        self.minimum_plate_width = self.settings.value(
            'cutting/min_width', defaultValue=50, type=int)
        self.guillotine_width = self.settings.value(
            'cutting/guillotine', defaultValue=1250, type=int)
        self.minimum_plate_length = self.settings.value(
            'cutting/min_length', defaultValue=100, type=int)
        self.maximum_plate_length = self.settings.value(
            'cutting/max_length', defaultValue=1300, type=int)
        self.cutting_thickness = self.settings.value(
            'cutting/cutting_thickness', defaultValue=4.2, type=float)
        self.clean_roll_height = self.settings.value(
            'rolling/clean_height', defaultValue=3, type=int)
        self.rough_roll_edge_loss = self.settings.value(
            'rolling/rough_edge', defaultValue=4, type=int)
        self.clean_roll_edge_loss = self.settings.value(
            'rolling/clean_edge', defaultValue=2, type=int)
        self.admissible_deformation = self.settings.value(
            'rolling/deformation', defaultValue=0.7, type=float)
        self.rough_roll_plate_width = self.settings.value(
            'rolling/max_rough_width', defaultValue=450, type=int)
        self.clean_roll_plate_width = self.settings.value(
            'rolling/max_clean_width', defaultValue=280, type=int)
        self.ingot_min_length = self.settings.value(
            'forging/min_forge_length', defaultValue=70, type=int)
        self.ingot_min_width = self.settings.value(
            'forging/min_forge_width', defaultValue=70, type=int)
        self.ingot_min_height = self.settings.value(
            'forging/min_forge_height', defaultValue=20.0, type=float)
        self.ingot_max_length = self.settings.value(
            'forging/max_forge_length', defaultValue=180, type=int)
        self.ingot_max_width = self.settings.value(
            'forging/max_forge_width', defaultValue=180, type=int)
        self.ingot_max_height = self.settings.value(
            'forging/max_forge_height', defaultValue=30.0, type=float)
        self.size_error = self.settings.value(
            'forging/size_error', defaultValue=2.0, type=float)
        self.allowance = self.settings.value(
            'forging/allowance', defaultValue=1.5, type=float)

    def write_settings(self) -> None:
        """Запись настроек в файл"""
        self.settings.setValue(
            'cutting/end_face', self.end_face_loss)
        self.settings.setValue(
            'cutting/cut_allowance', self.cut_allowance)
        self.settings.setValue(
            'cutting/guillotine', self.guillotine_width)
        self.settings.setValue(
            'cutting/min_width', self.minimum_plate_width)
        self.settings.setValue(
            'cutting/min_length', self.minimum_plate_length)
        self.settings.setValue(
            'cutting/max_length', self.maximum_plate_length)
        self.settings.setValue(
            'cutting/cutting_thickness', self.cutting_thickness)
        self.settings.setValue(
            'rolling/clean_height', self.clean_roll_height)
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
        self.settings.setValue(
            'forging/min_forge_length', self.ingot_min_length)
        self.settings.setValue(
            'forging/min_forge_width', self.ingot_min_width)
        self.settings.setValue(
            'forging/min_forge_height', self.ingot_min_height)
        self.settings.setValue(
            'forging/max_forge_length', self.ingot_max_length)
        self.settings.setValue(
            'forging/max_forge_width', self.ingot_max_width)
        self.settings.setValue(
            'forging/max_forge_height', self.ingot_max_height)
        self.settings.setValue(
            'forging/size_error', self.size_error)
        self.settings.setValue(
            'forging/allowance', self.allowance)

    def general_settings(self, order: Dict) -> Dict:
        return {
            'max_size': (
                (self.maximum_plate_length, self.clean_roll_plate_width),
                (self.maximum_plate_length, self.rough_roll_plate_width)
            ),
            'cutting_length': self.guillotine_width,
            'cutting_thickness': round(order['thickness'], 4),
            'hem_until_3': self.rough_roll_edge_loss,
            'hem_after_3': self.clean_roll_edge_loss,
            'allowance': self.cut_allowance,
            'end': round(self.end_face_loss, 4),
            'min_size': (self.minimum_plate_width, self.minimum_plate_length),
        }

    def forge_settings(self) -> Dict:
        return {
            'max_size': (self.ingot_max_length, self.ingot_max_width,
                         self.ingot_max_height),
            'min_size': (self.ingot_min_length, self.ingot_min_width,
                         self.ingot_min_height),
            'size_error': self.size_error,
            'allowance': self.allowance,
        }

    def save_tree(self, order: Dict, ingot: Dict, tree: Tree = None) -> None:
        """Сохранение корневого узла дерева"""
        file_name = self.get_file_name(order, ingot)
        path = 'schemes'
        abs_path = get_abs_path(file_name, path)
        with abs_path.open(mode='wb') as file:
            if tree:
                pickle.dump(tree, file)
            else:
                pickle.dump(self._tree, file)

    def is_file_exist(self, order: Dict, ingot: Dict):
        """Проверка существования файла"""
        file_name = self.get_file_name(order, ingot)
        path = 'schemes'
        abs_path = get_abs_path(file_name, path)
        return abs_path.exists()

    def scheme_count(self, order: Dict):
        dir_path = Path(__file__).parent.absolute()
        schemes_path = 'schemes'
        schemes_path = dir_path / schemes_path
        return len(list(schemes_path.glob(f'{order["id"]}_*.oci')))

    def load_tree(self, order: Dict, ingot: Dict) -> None:
        """Загрузка корневого узла дерева из файла"""
        file_name = self.get_file_name(order, ingot)
        path = 'schemes'
        abs_path = get_abs_path(file_name, path)
        with abs_path.open(mode='rb') as f:
            self._tree = pickle.load(f)

    def delete_tree(self, order: Dict, ingot: Dict = None) -> None:
        if ingot and self.is_file_exist(order, ingot):
            file_name = self.get_file_name(order, ingot)
            abs_path = get_abs_path(file_name, 'schemes')
            abs_path.unlink()
        else:
            abs_path = Path(__file__).parent / 'schemes'
            for path in abs_path.glob(f'{order["id"]}_*.oci'):
                path.unlink()

    def get_file_name(self, order: Dict, ingot: Dict) -> str:
        """Создание имени файла для сохранения дерева раскроя"""
        extension = 'oci'
        return f"{order['id']}_{ingot['id']}_{order['date']}.{extension}"


def get_abs_path(file_name: str, path=None) -> Path:
    """Получение абсолютного пути"""
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
    # изначальная формула
    number_of_trees = 4 * (4 ** num_of_heights - 1) / 3
    # экспериментально подобранная
    number_of_trees = 4 * (2 ** num_of_heights - 1) / 2
    if doubling:
        number_of_trees *= 2
        number = (2 ** num_of_heights * 2 - 2) / 2 + 1
    else:
        number = (2 ** num_of_heights - 1) / 2 + 1
    return int(number_of_trees + number)


def create_bins_residues(items, height: Number,
                         rolldir: Direction, material=None) -> List[Bin]:
    """Создание контейнеров из остатков

    :param items: список прямоуголников-остатков
    :type items: list[Rectangle]
    :param height: толщина
    :type height: Number
    :param rolldir: [description]
    :type rolldir: Direction
    :param material: материал, defaults to None
    :type material: Material, optional
    :return: Список контейнеров-остатков
    :rtype: list[Bin]
    """
    args = (height, rolldir, material, BinType.residue)
    return [Bin(item.length, item.width, *args) for item in items]


def incoming_rectangles(rect, height: float, kit: List[Any]):
    """Прямоугольники входящие в rect"""
    return [Rectangle3d(rect.length, rect.width, height).is_subrectangle(b, b.is_rotatable) for b in kit]


def filtration_residues(items: List, min_size: Tuple[Number, Number] = None, key=None):
    """Фильтрация остатков

    :param items: список прямоугольников
    :type items: list[Rectangle]
    :param min_size: минимальные размеры, defaults to None
    :type min_size: Optional[tuple[Number, Number]], optional
    :return: остатки с подходящими размерами
    :rtype: list[Rectangle]
    """
    key = key or (lambda x: x)
    residues = filter(lambda item: is_residual(key(item)), items)
    p_is_suitable_sizes = partial(is_suitable_sizes, min_size=min_size)
    if min_size:
        residues = filter(lambda item: p_is_suitable_sizes(key(item)), residues)
    return list(residues)


def debug_visualize(node, name):
    # NOTE: своя визуализация для отладки
    from sequential_mh.tsh import rect
    from sequential_mh.tsh.est import Estimator
    from sequential_mh.tsh.visualize import visualize
    main_rect = rect.Rectangle.create_by_size(
        (0, 0), node.bin.length, node.bin.width
    )
    main_region = Estimator(main_rect, node.bin.height, node.bin.height)
    rectangles = list(chain.from_iterable(node.result.blanks.values()))
    visualize(
        main_region, rectangles, node.result.tailings,
        xlim=node.bin.width + 50, ylim=node.bin.length + 50,
        prefix=name
    )


def debug_graph_tree(tree, name=''):
    # NOTE: своя визуализация дерева, удалить по завершении
    import os
    os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin'
    from sequential_mh.bpp_dsc.graph import plot, create_edges
    if not name:
        name = 'tree'
    graph1, all_nodes1 = plot(tree.root, f'pdf/{name}.gv')
    create_edges(graph1, all_nodes1)
    graph1.view()
    k = 0
    for node in tree.root.cc_leaves:
        print(f'Количество заготовок в осн. узле: {len(node.placed)}')
        for subtree in node.subtree:
            placed = 0
            for subnode in subtree.root.cc_leaves:
                placed += len(subnode.placed)
            print(f'\tКоличество заготовок в поддереве: {placed}')
            graph1, all_nodes1 = plot(subtree.root, f'pdf/{name}_subtree{k}.gv')
            create_edges(graph1, all_nodes1)
            graph1.view()
            k+=1
    print(f'Количество поддеревьев: {k}')


def is_residual(item) -> bool:
    """Проверка на остаток

    :param item: Прямоугольник тип которого проверяется
    :type item: Rectangle
    :return: True если остаток и False в противном случае
    :rtype: bool
    """
    return isinstance(item, Bin) or item.rtype == RectangleType.RESIDUAL


def is_suitable_sizes(item, min_size: Tuple[Number, Number]) -> bool:
    """Проверка минимальных размеров

    :param item: Прямоугольник
    :type item: Rectangle
    :param min_size: Минимальные размеры в формате (length, width)
    :type min_size: tuple[Number, Number]
    :return: True если прямоугольник удовлетворяет минимальным размерам
             и False в противном случае
    :rtype: bool
    """
    if isinstance(item, Bin):
        min_side = min(item.size[:2])
        max_side = max(item.size[:2])
    else:
        min_side = item.min_side
        max_side = item.max_side
    return min_side >= min(min_size) and max_side >= max(min_size)


def save_tailing(length, width, height, material, batch):
    fusions = CatalogDataService.fusions_list()
    fusion = fusions[material.name]

    statuses = IngotStatusDataService.get_by_name('Остаток')
    if statuses:
        status = statuses[0]
    else:
        raise ValueError('Статус "Остаток" не найден')

    # делаем остаток
    _id = StandardDataService.save_record(
        'ingots', fusion_id=fusion, batch=batch, status_id=status.id_,
        length=int(length), width=int(width),
        height=height
    )
    print(f'Остаток сохранен: {_id = }')


if __name__ == '__main__':
    setup_logging()
    logging.info('Приложение OCI запущено.')
    start = time.time()
    application = QApplication(sys.argv)

    main_window = OCIMainWindow()
    main_window.show()

    exit_code = application.exec()

    total_time = time.time() - start
    # print(f'{start = }, {total_time = }')
    logging.info(
        'Выход из приложения OCI. Время работы: %(time).2f мин.',
        {'time': total_time / 60}
    )

    sys.exit(exit_code)
