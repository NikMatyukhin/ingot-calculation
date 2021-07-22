"""Модуль главного окна"""


import copy
import sys
import pickle
import logging
import time
import math
from typing import Dict, Union
from itertools import chain
from functools import partial
from collections import Counter, deque, namedtuple
from pathlib import Path

from PyQt5.QtCore import (
    Qt, QSettings, QModelIndex
)
from PyQt5.QtWidgets import (
    QApplication, QGraphicsView, QMainWindow, QTableWidget, QTableWidgetItem,
    QMessageBox, QDialog, QVBoxLayout, QGraphicsScene, QLayout, QProgressDialog
)

from gui import ui_mainwindow
from gui.ui_functions import *
from widgets import (
    IngotSectionDelegate, ListValuesDelegate, ExclusiveButton,
    OrderSectionDelegate
)
from models import (
    IngotModel, OrderInformationComplectsModel, OrderModel
)
from service import (
    Field, OrderDataService, StandardDataService, UpdatableFieldsCollection,
    CatalogDataService, IngotStatusDataService
)
from dialogs import (
    IngotAddingDialog, IngotAssignmentDialog, IngotReadinessDialog, OrderAddingDialog,
    FullScreenWindow, OrderEditingDialog
)
from storage import Storage
from charts.plan import CuttingPlanPainter, MyQGraphicsView
from charts.map import CuttingMapPainter
from catalog import Catalog
from settings import SettingsDialog
from exceptions import ForcedTermination
from log import setup_logging, timeit, log_operation_info

from sequential_mh.bpp_dsc.rectangle import (
    BinType, Direction, Material, Blank, Kit, Bin, Rectangle3d
)
from sequential_mh.bpp_dsc.tree import (
    BinNode, Tree, solution_efficiency, is_defective_tree, is_cc_node,
    get_all_residuals, get_residuals
)
from sequential_mh.bpp_dsc.exception import BPPError
from sequential_mh.bpp_dsc.support import dfs
from sequential_mh.bpp_dsc.stm import (
    _pack, _create_insert_template, predicate, is_empty_tree, is_empty_node
)
from sequential_mh.tsh.rect import RectangleType


Number = Union[int, float]
Sizes = tuple[Number, Number, Number]
ListSizes = list[Sizes]


class OCIMainWindow(QMainWindow):
    """Главное окно"""
    def __init__(self):
        super().__init__()
        self.ui = ui_mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)

        # Установка визуальных дополнений приложения
        UIFunctions.setApplicationStyles(self)
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setColor(QColor(0, 0, 0))
        self.shadow_effect.setYOffset(-5)
        self.shadow_effect.setXOffset(0)
        self.shadow_effect.setBlurRadius(20)
        self.ui.topBar.setGraphicsEffect(self.shadow_effect)
        self.shadow_effect_2 = QGraphicsDropShadowEffect()
        self.shadow_effect_2.setColor(QColor(0, 0, 0))
        self.shadow_effect_2.setYOffset(-5)
        self.shadow_effect_2.setXOffset(0)
        self.shadow_effect_2.setBlurRadius(20)
        self.ui.order_name.setGraphicsEffect(self.shadow_effect_2)

        # Модель и делегат заказов
        self.order_model = OrderModel(Field('status_id', 1), self)
        self.order_delegate = OrderSectionDelegate(self.ui.searchResult_1)
        self.ui.searchResult_1.setModel(self.order_model)
        self.ui.searchResult_1.setItemDelegate(self.order_delegate)
        self.order_delegate.deleteIndexClicked.connect(self.confirm_order_removing)

        # Модель слитков (обновляется при изменении текущего заказа)
        # TODO: пока заказ не выбран пусть содержит свободные слитки,
        #       чтобы потом показывать их на главном экране - пойдёт на склад
        self.ingot_model = IngotModel('unused')
        self.ingot_delegate = IngotSectionDelegate(self.ui.ingotsView)
        self.ui.ingotsView.setModel(self.ingot_model)
        self.ui.ingotsView.setItemDelegate(self.ingot_delegate)
        self.ui.ingotsView.clicked.connect(self.show_ingot_information)
        self.ingot_delegate.forgedIndexClicked.connect(self.confirm_ingot_readiness)
        self.ingot_delegate.deleteFromOrderClicked.connect(self.confirm_ingot_removing)

        # Модель комплектов (обновляется при изменении текущего заказа)
        # Не содержит ничего, пока не установлен идентификатор заказа
        self.complect_headers = [
            'Название', 'ID', 'Статус', 'Сплав', 'Длина', 'Ширина', 'Толщина',
            'Количество', 'Упаковано', 'Приоритет', 'Направление проката'
        ]
        self.complect_model = OrderInformationComplectsModel(self.complect_headers)
        
        self.statuses_list = CatalogDataService.statuses_list()
        self.directions_list = CatalogDataService.directions_list()
        self.fusions_list = CatalogDataService.fusions_list()
        self.status_delegate = ListValuesDelegate(self.statuses_list)
        self.direction_delegate = ListValuesDelegate(self.directions_list)
        self.fusion_delegate = ListValuesDelegate(self.fusions_list)
        self.ui.complectsView.setItemDelegateForColumn(2, self.status_delegate)
        self.ui.complectsView.setItemDelegateForColumn(3, self.fusion_delegate)
        self.ui.complectsView.setItemDelegateForColumn(10, self.direction_delegate)
        for column in range(self.complect_model.columnCount(QModelIndex())):
            self.ui.complectsView.resizeColumnToContents(column)
        
        self.ui.complectsView.setModel(self.complect_model)

        # Дерево раскроя
        self.tree = None

        # Работа с настройками приложения: подгрузка настроек
        self.settings = QSettings('configs', QSettings.IniFormat, self)
        self.is_saved = True

        self.cut_allowance = 0             # Припуск на разрез
        self.end_face_loss = 0             # Потери при обработке торцов (%)
        self.minimum_plate_width = 0       # Минимальная ширина пластины
        self.minimum_plate_height = 0      # Минимальная длина пластины
        self.rough_roll_edge_loss = 0      # Потери при обработке кромки до 3мм
        self.clean_roll_edge_loss = 0      # Потери при обработке кромки на 3мм

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

        # Соединяем сигналы окна со слотами класса
        self.ui.newOrder.clicked.connect(self.open_order_dialog)
        self.ui.catalog.clicked.connect(self.open_catalog_window)
        self.ui.settings.clicked.connect(self.open_settings_dialog)
        self.ui.storage.clicked.connect(self.open_storage_window)
        self.ui.newIngot.clicked.connect(self.open_ingot_dialog)
        self.ui.assign_ingot.clicked.connect(self.open_assign_dialog)
        self.ui.edit_order.clicked.connect(self.open_edit_dialog)

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
        self.ui.recalculate.clicked.connect(self.create_tree)

    def show_order_information(self, index: QModelIndex):
        """Переключатель активных заказов и открытых секций.

        Отвечает за то, чтобы одновременно была раскрыта только одна секция
        из списка заказов. Подгружает новую страницу заказа при его выборе.
        """
        if not index.isValid():
            return
        order = index.data(Qt.DisplayRole)

        self.ingot_model.order = order['id']
        self.ui.ingotsView.setCurrentIndex(self.ingot_model.index(0, 0, QModelIndex()))
        self.show_ingot_information(self.ui.ingotsView.currentIndex())
        self.complect_model.order = order['id']
        self.ui.complectsView.setColumnHidden(1, True)
        self.ui.complectsView.setColumnWidth(0, 210)
        self.ui.complectsView.setColumnWidth(2, 115)
        self.ui.complectsView.setColumnWidth(3, 90)
        self.ui.complectsView.setColumnWidth(4, 55)
        self.ui.complectsView.setColumnWidth(5, 65)
        self.ui.complectsView.setColumnWidth(6, 70)
        self.ui.complectsView.setColumnWidth(7, 85)
        self.ui.complectsView.setColumnWidth(8, 75)
        self.ui.complectsView.setColumnWidth(9, 85)
        self.ui.complectsView.expandAll()

        self.ui.order_name.setText('Заказ ' + order['name'])

        self.map_scene.clear()

        ingot = self.ui.ingotsView.currentIndex().data(Qt.DisplayRole)
        if ingot and self.is_file_exist(order, ingot):
            self.load_tree(order, ingot)
            self.redraw_map(ingot)

        self.ui.orderInformationArea.setCurrentWidget(self.ui.informationPage)

    def show_ingot_information(self, current: QModelIndex):
        ingot = current.data(Qt.DisplayRole)
        order = self.ui.searchResult_1.currentIndex().data(Qt.DisplayRole)
        if not ingot or not order:
            return
        if ingot['status_id'] == 3:
            self.ui.recalculate.setEnabled(False)
        else:
            self.ui.recalculate.setEnabled(True)
        if self.is_file_exist(order, ingot):
            self.load_tree(order, ingot)
            self.redraw_map(ingot)
        else:
            self.map_scene.clear()

    def confirm_ingot_readiness(self, index: QModelIndex):
        """Подтверждение готовности слитка.

        :param index: Индекс подтверждаемого слитка
        :type index: QModelIndex
        """
        ingot = self.ingot_model.data(index, Qt.DisplayRole)
        fusion_name = StandardDataService.get_by_id('fusions', Field('id', ingot['fusion_id']))[1]
        sizes = ingot['size']
        # Запрос данных о готовности слитка
        window = IngotReadinessDialog(ingot['id'], sizes, fusion_name, self)
        if window.exec_() == QDialog.Accepted:
            # Заказ возможно стоит сделать обычным и готовым
            self.ingot_model.setData(index, {'status_id': 1, 'batch': window.get_batch()}, Qt.EditRole)
            self.check_current_order()
            # ingot = self.unused_ingots_model.data(index, Qt.DisplayRole)

    def confirm_ingot_removing(self, index: QModelIndex):
        ingot = self.ingot_model.data(index, Qt.DisplayRole)
        order = self.ui.searchResult_1.currentIndex().data(Qt.DisplayRole)

        message = QMessageBox(self)
        message.setWindowTitle('Подтверждение удаления')
        message.setText(f'Вы уверены, что хотите удалить этот слиток?')
        message.setIcon(QMessageBox.Icon.Question)
        answer = message.addButton('Да', QMessageBox.ButtonRole.AcceptRole)
        message.addButton('Отмена', QMessageBox.ButtonRole.RejectRole)
        message.exec()

        if answer == message.clickedButton():
            if ingot['status_id'] == 3:
                success = StandardDataService.delete_by_id('ingots', Field('id', ingot['id']))
            elif ingot['status_id'] in [1, 2]:
                success = StandardDataService.update_record('ingots', Field('id', ingot['id']), order_id=None)
            if not success:
                QMessageBox.critical(self, 'Ошибка удаления', 'Не удалось удалить слиток.', QMessageBox.Ok)
                return
            self.ingot_model.deleteRow(index.row())
            self.complect_model.discard_statuses(order['id'], ingot['fusion_id'])
            self.ui.complectsView.expandAll()
            try:
                order_efficiency = OrderDataService.efficiency(Field('order_id', order['id']))
            except ZeroDivisionError:
                order_efficiency = 0
                self.map_scene.clear()
            self.order_model.setData(self.ui.searchResult_1.currentIndex(), {'efficiency': order_efficiency}, Qt.EditRole)
            StandardDataService.update_record('orders', Field('id', order['id']), efficiency=order_efficiency)

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
            StandardDataService.update_record('orders', Field('id', order_index.data(Qt.DisplayRole)['id']), status_id=1)

    def confirm_order_adding(self, data: dict):
        self.order_model.appendRow(data)

    def confirm_order_editing(self, data: dict):
        index = self.ui.searchResult_1.currentIndex()
        self.order_model.setData(index, data, Qt.EditRole)
        self.show_order_information(index)

    def confirm_order_removing(self, index: QModelIndex):
        order = index.data(Qt.DisplayRole)

        # FIXME: вариант в одну строку им не нравится, так как у кнопок текст
        #        не "Да" + "Отмена", а "Ok" + "Cancel"
        message = QMessageBox(self)
        message.setWindowTitle('Подтверждение удаления')
        message.setText(f'Вы уверены, что хотите удалить заказ "{order["name"]}"?')
        message.setIcon(QMessageBox.Icon.Question)
        answer = message.addButton('Да', QMessageBox.ButtonRole.AcceptRole)
        message.addButton('Отмена', QMessageBox.ButtonRole.RejectRole)
        message.exec()
        # FIXME: если можно короче, сделаю короче, пока хз

        if answer == message.clickedButton():
            success = StandardDataService.delete_by_id('orders', Field('id', order['id']))
            if not success:
                QMessageBox.critical(self, 'Ошибка удаления', 'Не удалось удалить заказ.', QMessageBox.Ok)
                return
            self.order_model.deleteRow(index.row())
            self.ui.orderInformationArea.setCurrentWidget(self.ui.defaultPage)
        self.ui.searchResult_1.clearSelection()

    def update_complect_statuses(self, order_id: int, ingot_fusion: int):
        """Обновление статусов заготовок"""
        # Подсчитываем количество неразмещенных заготовок (название: количество)
        unplaced_counter = Counter(b.name for b in self.tree.kit)
        for leave in self.tree.cc_leaves:
            unplaced_counter -= Counter(b.name for b in leave.placed)

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
                complect_counter[article_name + '_' + name] = {
                    'detail_id': int(model.data(model.index(sub_row, 1, article), Qt.DisplayRole)),
                    'depth': float(model.data(model.index(sub_row, 6, article), Qt.DisplayRole)),
                    'amount': int(model.data(model.index(sub_row, 7, article), Qt.DisplayRole)),
                    'status_id': model.index(sub_row, 2, article),
                    'total': model.index(sub_row, 8, article)
                }

        # Сначала проходимся по счётчику неразмещённых заготовок
        updates = UpdatableFieldsCollection(['status_id', 'total', 'order_id', 'detail_id'])
        order = Field('order_id', order_id)

        for name in unplaced_counter:
            detail = Field('detail_id', complect_counter[name]['detail_id'])

            # Если количество заготовок совпадает с остатком
            if complect_counter[name]['amount'] == unplaced_counter[name]:
                updates.append(Field('status_id', 4), Field('total', 0), order, detail)
                model.setData(complect_counter[name]['status_id'], 4, Qt.EditRole)
                model.setData(complect_counter[name]['total'], 0, Qt.EditRole)
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

    def save_complects(self):
        text = self.ui.saveComplect.text()
        if text.endswith('*'):
            order_id = self.ui.searchResult_1.currentIndex().data(Qt.DisplayRole)['id']
            order = Field('order_id', order_id)

            updates = UpdatableFieldsCollection(['amount', 'priority', 'order_id', 'detail_id'])
            model = self.complect_model

            for row in range(model.rowCount(QModelIndex())):
                article_index = model.index(row, 0, QModelIndex())

                for sub_row in range(model.rowCount(article_index)):
                    detail_index = model.index(sub_row, 1, article_index)
                    amount_index = model.index(sub_row, 7, article_index)
                    priority_index = model.index(sub_row, 8, article_index)

                    detail = Field('detail_id', model.data(detail_index, Qt.DisplayRole))
                    amount = Field('amount', model.data(amount_index, Qt.DisplayRole))
                    priority = Field('priority', model.data(priority_index, Qt.DisplayRole))
                    updates.append(amount, priority, order, detail)
            OrderDataService.update_complects(updates)
            self.ui.saveComplect.setText(text[:-1])

    def safe_create_tree(self):
        """Сохранение дерева"""
        self.save_complects()
        self.create_tree()

    def create_tree(self):
        # Пока работаем только с одном слитком
        order = self.ui.searchResult_1.currentIndex().data(Qt.DisplayRole)
        ingot = self.ui.ingotsView.currentIndex().data(Qt.DisplayRole)
        fusion_name = StandardDataService.get_by_id('fusions', Field('id', ingot['fusion_id']))[1]

        # TODO: Вторым аргументом нужно вставить плотность сплава
        material = Material(fusion_name, 2.2, 1.)

        # Выбор заготовок и удаление лишних значений
        details = None
        try:
            details = self.get_details_kit(material)
        except Exception as exception:
            QMessageBox.critical(self, 'Ошибка сборки', f'{exception}', QMessageBox.Ok)
            return
        # Отображение прогресса раскроя
        progress = QProgressDialog('OCI', 'Закрыть', 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle('Раскрой')
        progress.forceShow()
        order_name = order['name']
        ingot_size = ingot['size']
        order_id = int(order['id'])
        log_operation_info(
            'create_cut', {'name': order_name, 'alloy': fusion_name},
            identifier=order_id
        )
        progress.setLabelText('Процесс раскроя...')
        try:
            log_operation_info(
                'cut_info',
                {
                    'name': order_name, 'alloy': fusion_name,
                    'size': 'x'.join(map(str, ingot_size)),
                    'blanks': details.qty(), 'heights': len(details.keys())
                }, identifier=order_id
            )
            _, efficiency, _ = self.create_cut(
                ingot_size, details, material, progress=progress
            )
            self.save_residuals()
        except ForcedTermination:
            log_operation_info(
                'user_inter_cut', {'name': order_name, 'alloy': fusion_name},
                identifier=order_id
            )
            QMessageBox.information(self, 'Внимание', 'Процесс раскроя был прерван!', QMessageBox.Ok)
            return
        except Exception as exception:
            QMessageBox.critical(
                self, 'Раскрой завершился с ошибкой', f'{exception}', QMessageBox.Ok
            )
            return
        else:
            progress.setLabelText('Завершение раскроя...')

            ingot_index = self.ui.ingotsView.currentIndex()
            self.ingot_model.setData(ingot_index, {'efficiency': round(efficiency, 2)}, Qt.EditRole)
            StandardDataService.update_record(
                'ingots', Field('id', ingot_index.data(Qt.DisplayRole)['id']), efficiency=round(efficiency, 2)
            )

            order_index = self.ui.searchResult_1.currentIndex()

            self.update_complect_statuses(
                order_index.data(Qt.DisplayRole)['id'],
                ingot_index.data(Qt.DisplayRole)['fusion_id']
            )

            order_efficiency = OrderDataService.efficiency(Field('order_id', order_index.data(Qt.DisplayRole)['id']))
            self.order_model.setData(order_index, {'efficiency': order_efficiency}, Qt.EditRole)
            StandardDataService.update_record(
                'orders', Field('id', order_index.data(Qt.DisplayRole)['id']), efficiency=order_efficiency
            )

            order = self.ui.searchResult_1.currentIndex().data(Qt.DisplayRole)
            ingot = self.ui.ingotsView.currentIndex().data(Qt.DisplayRole)
            self.save_tree(order, ingot)
            self.redraw_map(ingot)

            log_operation_info(
                'end_cut',
                {
                    'name': order_name, 'alloy': fusion_name,
                    'efficiency': efficiency, 'total_efficiency': order_efficiency
                }, identifier=order_id
            )
        progress.close()

    def redraw_map(self, ingot: Dict):
        self.map_scene.clear()
        self.map_painter.setTree(self.tree)
        self.map_painter.setEfficiency(round(ingot['efficiency'], 2))
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
                sizes: Sizes = [length, width, depth]
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

        # NOTE: своя визуализация для отладки
        # for node in self.tree.cc_leaves:
        #     debug_visualize(node, 'Основной')
        #     if node.subtree:
        #         for subtree in node.subtree:
        #             for subnode in subtree.root.cc_leaves:
        #                 debug_visualize(subnode, f'Остаток от {node.bin.height} мм')

        efficiency = solution_efficiency(self.tree, list(dfs(self.tree)), tree.main_kit, is_total=True)

        return tree, efficiency, .1

    @timeit
    def stmh_idrd(self, tree, with_filter: bool = True,
                  restrictions: dict = None, progress: QProgressDialog = None,
                  level_subtree=0, with_priority=True):
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

        if not trees:
            raise BPPError('Не удалось получить раскрой')

        print(f'Годных деревьев: {len(trees)}')
        if progress:
            progress.setLabelText('Выбор оптимального решения...')

        # отладочная визуализация
        # import os
        # os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin'
        # from sequential_mh.bpp_dsc.graph import plot, create_edges
        # for i, tree in enumerate(trees):
        #     print(f'Дерево {i}:')
        #     for node in tree.root.cc_leaves:
        #         print(f'{node.bin.height}: {len(node.placed)}')
        #     # graph1, all_nodes1 = plot(tree.root, f'pdf/graph{i}.gv')
        #     # create_edges(graph1, all_nodes1)
        #     # graph1.view()
        #     ef_1 = solution_efficiency(
        #         tree.root, list(dfs(tree.root)), tree.main_kit, nd=True, is_p=False
        #     )
        #     print(f'Эффективность без приоритета {ef_1}')
        #     ef_2 = solution_efficiency(
        #         tree.root, list(dfs(tree.root)), tree.main_kit, nd=True, is_p=True
        #     )
        #     print(f'Эффективность c приоритетом {ef_2}')
        #     print('-' * 50)
        best = max(
            trees, key=lambda item: solution_efficiency(
                item.root, list(dfs(item.root)), item.main_kit, nd=True, is_p=True
            )
        )
        for node in best.root.cc_leaves:
            print(node.bin.height, node._id)
        get_all_residuals(best)
        return best

    # @staticmethod
    def _stmh_idrd(self, tree, local: bool = False, with_filter: bool = True,
                   restrictions: dict = None,
                   progress: QProgressDialog = None, end_progress=True,
                   direction=1, start_step=0, steps=0,
                   level_subtree=0, with_priority=True):
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
            new_level = deque([])
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
            nodes = [
                node for node in tree.root.leaves() if not is_empty_node(node)
            ]
            nodes = deque(sorted(nodes, key=predicate))
            node = nodes[0]
            if is_cc_node(node):
                _pack(node, level, restrictions, with_priority=with_priority)
                # контролируем уровень построения поддеревьев
                # FIXME: раскоментировать для учета остатков
                # if tree._type == 0:
                #     level_subtree = 0
                # if level_subtree < 1:
                #     level_subtree += 1
                #     self.create_subtree(node, restrictions, level_subtree)
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

    def create_subtree(self, node, restrictions, level_subtree):
        """Создание поддерева для остатка

        :param node: Узел, содержащий остатки
        :type node: CuttingChartNode
        :param restrictions: Ограничения
        :type restrictions: dict
        :param level_subtree: Уровень поддерева, ограничивает
                              рекурсивное построение деревьев
        :type level_subtree: int
        """
        min_size = self.minimum_plate_height, self.minimum_plate_width
        tailings = get_residuals(node)
        tailings = filtration_residues(node.result.tailings, min_size=min_size)
        suitable_residues = [
            t for t in tailings
            if incoming_rectangles(t, node.bin.height, node.result.unplaced)
        ]
        # если нет прямоугольников для размещения текущей
        # толщины пробуем упаковать другие
        adjacent_branch = node.adjacent_branch()
        adj_node = adjacent_branch.adj_leaves[0]
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
                new_tree = self.stmh_idrd(
                    new_tree, restrictions=restrictions,
                    level_subtree=level_subtree, with_priority=False
                )
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
        best = max(
            trees,
            key=lambda item: solution_efficiency(
                item.root, list(dfs(item.root)), item.main_kit, nd=True, is_p=True
            )
        )
        get_all_residuals(best)

        # NOTE: своя визуализация для отладки
        # for node in best.root.cc_leaves:
        #     debug_visualize(node, 'Основной')
        #     if node.subtree:
        #         for subtree in node.subtree:
        #             for subnode in subtree.root.cc_leaves:
        #                 debug_visualize(subnode, f'Остаток от {node.bin.height} мм')
        return best

    def save_residuals(self):
        """Сохранение остатков в БД"""
        # по второму кругу получаем слиток для определения партии
        ingot = self.ui.ingotsView.currentIndex().data(Qt.DisplayRole)
        # гемор с партией, без ООП тяжко
        batch = ingot['batch']
        order_id = ingot['order_id']
        min_size = self.minimum_plate_height, self.minimum_plate_width
        if self.tree is None:
            raise ValueError('Дерево не рассчитано')
        for node in self.tree.cc_leaves:
            tailings = filtration_residues(node.result.tailings, min_size=min_size)
            print(f'Остатки для толщины {node.result.height}: {len(tailings)} шт')
            for i, tailing in enumerate(tailings):
                print(f'\t{i:< 4}{tailing.length, tailing.width}; {tailing.rtype}; {node.bin.material}')

                # получаем сплав
                fusions = CatalogDataService.fusions_list()
                fusion = fusions[node.bin.material.name]

                statuses = IngotStatusDataService.get_by_name('Остаток')
                if statuses:
                    status = statuses[0]
                else:
                    raise ValueError('Статус "Остаток" не найден')

                # делаем остаток
                _id = StandardDataService.save_record(
                    'ingots', fusion_id=fusion, batch=batch, status_id=status.id_,
                    length=tailing.length, width=tailing.width,
                    height=node.bin.height
                )
                print(f'Остаток сохранен: {_id = }')
                # прявязка к заказу

    def steps(self):
        """Список толщин"""
        leaves = self.tree.cc_leaves
        depth_list = [leave.bin.height for leave in leaves]
        return depth_list

    def chartPagePreparation(self):
        """Подготовка страницы с планами раскроя"""
        # order = self.ui.searchResult_1.currentIndex().data(Qt.DisplayRole)
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

        # Кнопку завершения заказа меняем на кнопку перехода на след.шаг
        # depth = order['current_depth']
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
        order = self.ui.searchResult_1.currentIndex().data(Qt.DisplayRole)
        self.graphicsView.setScene(self.plan_scene)
        pack = self.tree.cc_leaves[index]
        depth = pack.bin.height
        self.plan_painter.setBin(
            math.ceil(pack.bin.length),
            math.ceil(pack.bin.width),
            round(pack.bin.height, 1)
        )
        for blank in pack.result:
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
        self.loadDetailList(depth=float(depth))

    def loadDetailList(self, depth: float):
        """Подгрузка списка заготовок"""
        # TODO: классика, переделать на model/view
        # order = self.ui.searchResult_1.currentIndex().data(Qt.DisplayRole)
        self.clearLayout(self.ui.verticalLayout_8, hidden=True)
        # cut_blanks = OrderDataService.cut_blanks({'order_id': order['order_id']}, depth)
        # for detail in cut_blanks:
        #     detail_section = Section(detail[0], detail[1])
        #     detail_section.setContentFields(
        #         self.createDetailTable(*detail[2:])
        #     )
        #     self.ui.verticalLayout_8.insertWidget(0, detail_section)

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
        """Метод для очистки слоёв компоновки

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
        window.show()

    def open_storage_window(self):
        """Работа с хранилищем (складом) слитков"""
        window = Storage(self)
        window.show()

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

    def open_assign_dialog(self):
        """Добавление слитка к заказу"""
        order = self.ui.searchResult_1.currentIndex().data(Qt.DisplayRole)
        window = IngotAssignmentDialog(order, self)
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
        ingot_settings = {
            'max_size': (self.ingot_max_height, self.ingot_max_width, self.ingot_max_depth),
            'min_size': (self.ingot_min_height, self.ingot_min_width, self.ingot_min_depth),
            'size_error': self.size_error,
            'allowance': self.allowance,
        }
        window.set_settings(settings, ingot_settings)
        window.predictedIngotSaved.connect(self.save_tree)
        if window.exec() == QDialog.Accepted:
            efficiency = OrderDataService.efficiency(Field('order_id', order['id']))
            self.order_model.setData(self.ui.searchResult_1.currentIndex(), {'efficiency': efficiency}, Qt.EditRole)
            StandardDataService.update_record('orders', Field('id', order['id']), efficiency=efficiency)
        self.show_order_information(self.ui.searchResult_1.currentIndex())

    def open_order_dialog(self):
        """Добавление нового заказа"""
        window = OrderAddingDialog(self)
        window.recordSavedSuccess.connect(self.confirm_order_adding)
        window.exec_()

    def open_edit_dialog(self):
        """Изменение текущего заказа"""
        order = self.ui.searchResult_1.currentIndex().data(Qt.DisplayRole)
        window = OrderEditingDialog(order, self.complect_model, self)
        window.orderEditedSuccess.connect(self.confirm_order_editing)
        window.show()

    def read_settings(self):
        """Чтение настроек из файл"""
        self.cut_allowance = self.settings.value(
            'cutting/cut_allowance', defaultValue=2, type=int)
        self.end_face_loss = self.settings.value(
            'cutting/end_face', defaultValue=0.01, type=float)
        self.minimum_plate_width = self.settings.value(
            'cutting/min_width', defaultValue=50, type=int)
        self.guillotine_width = self.settings.value(
            'cutting/guillotine', defaultValue=1200, type=int)
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
        self.ingot_min_height = self.settings.value(
            'forging/min_height', defaultValue=70, type=int)
        self.ingot_min_width = self.settings.value(
            'forging/min_width', defaultValue=70, type=int)
        self.ingot_min_depth = self.settings.value(
            'forging/min_depth', defaultValue=20.0, type=float)
        self.ingot_max_height = self.settings.value(
            'forging/max_height', defaultValue=180, type=int)
        self.ingot_max_width = self.settings.value(
            'forging/max_width', defaultValue=180, type=int)
        self.ingot_max_depth = self.settings.value(
            'forging/max_depth', defaultValue=30.0, type=float)
        self.size_error = self.settings.value(
            'forging/size_error', defaultValue=2.0, type=float)
        self.allowance = self.settings.value(
            'forging/allowance', defaultValue=1.5, type=float)

    def write_settings(self):
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
        self.settings.setValue(
            'forging/min_height', self.ingot_min_height)
        self.settings.setValue(
            'forging/min_width', self.ingot_min_width)
        self.settings.setValue(
            'forging/min_depth', self.ingot_min_depth)
        self.settings.setValue(
            'forging/max_height', self.ingot_max_height)
        self.settings.setValue(
            'forging/max_width', self.ingot_max_width)
        self.settings.setValue(
            'forging/max_depth', self.ingot_max_depth)
        self.settings.setValue(
            'forging/size_error', self.size_error)
        self.settings.setValue(
            'forging/allowance', self.allowance)

    def save_tree(self, order: Dict, ingot: Dict, tree: Tree = None):
        """Сохранение корневого узла дерева"""
        file_name = self.get_file_name(order, ingot)
        path = 'schemes'
        abs_path = get_abs_path(file_name, path)
        with abs_path.open(mode='wb') as file:
            if tree:
                pickle.dump(tree, file)
            else:
                pickle.dump(self.tree, file)

    def is_file_exist(self, order: Dict, ingot: Dict):
        """Проверка существования файла"""
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
        return f"{order['id']}_{ingot['id']}_{order['date']}.{extension}"


def get_abs_path(file_name, path=None) -> Path:
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
                         rolldir: Direction, material=None) -> list[Bin]:
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


def incoming_rectangles(rect, height, kit):
    """Прямоугольники входящие в rect"""
    return [Rectangle3d(rect.length, rect.width, height).is_subrectangle(b, b.is_rotatable) for b in kit]


def filtration_residues(items, min_size=None):
    """Фильтрация остатков

    :param items: список прямоугольников
    :type items: list[Rectangle]
    :param min_size: минимальные размеры, defaults to None
    :type min_size: Optional[tuple[Number, Number]], optional
    :return: остатки с подходящими размерами
    :rtype: list[Rectangle]
    """
    residues = filter(is_residual, items)
    p_is_suitable_sizes = partial(is_suitable_sizes, min_size=min_size)
    if min_size:
        residues = filter(p_is_suitable_sizes, residues)
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


def is_residual(item) -> bool:
    """Проверка на остаток

    :param item: Прямоугольник тип которого проверяется
    :type item: Rectangle
    :return: True если остаток и False в противном случае
    :rtype: bool
    """
    return item.rtype == RectangleType.RESIDUAL


def is_suitable_sizes(item, min_size: tuple[Number, Number]) -> bool:
    """Проверка минимальных размеров

    :param item: Прямоугольник
    :type item: Rectangle
    :param min_size: Минимальные размеры в формате (length, width)
    :type min_size: tuple[Number, Number]
    :return: True если прямоугольник удовлетворяет минимальным размерам
             и False в противном случае
    :rtype: bool
    """
    return item.min_side >= min(min_size) and item.max_side >= max(min_size)


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
