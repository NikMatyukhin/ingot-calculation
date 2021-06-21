from enum import unique
import math
import logging
import typing
from datetime import datetime
from typing import Dict, List, Union

from PySide6.QtCore import (
    QPoint, QTimer, Qt, Signal, QPointF, QModelIndex
)
from PySide6.QtGui import (
    QIntValidator, QAction
)
from PySide6.QtWidgets import (
    QDialog, QCompleter, QGraphicsScene, QMessageBox, QMenu, QToolTip, QWidget,
    QGraphicsDropShadowEffect, QProgressDialog
)

from sequential_mh.bpp_dsc.rectangle import (
    Direction, Material, Blank, Kit, Bin
)
from sequential_mh.bpp_dsc.tree import (
    BinNode, Tree, solution_efficiency
)
# from sequential_mh.bpp_dsc.prediction import optimal_ingot_size
from sequential_mh.bpp_dsc.support import dfs
from gui import (
    ui_add_product_dialog, ui_add_article_dialog, ui_add_detail_dialog,
    ui_add_order_dialog, ui_add_ingot_dialog, ui_full_screen,
    ui_ready_ingot_dialog
)
from service import (
    DirectionDataService, FusionDataService, OrderDataService,
    ProductDataService, StandardDataService
)
from models import (
   ArticleInformationFilterProxyModel, OrderComplectsFilterProxyModel,
   ComplectsModel, IngotModel
)
from widgets import (
    IngotSectionDelegate
)
from exceptions import ForcedTermination


Number = Union[int, float]
Sizes = tuple[Number, Number, Number]


class ProductDialog(QDialog):
    """Диалоговое окно добавления новой продукции.
    
    После добавления новой продукции посылает сигнал с параметрами для того,
    чтобы основное окно каталога обновило данные в модели.
    """
    
    recordSavedSuccess = Signal(list)

    def __init__(self, parent):
        super(ProductDialog, self).__init__(parent)
        self.ui = ui_add_product_dialog.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle('Добавление продукции')
        
        # Таймер для подсветки ошибки
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.cooldown)
        self.duration = 1500
        self.tip = "Поле необходимо заполнить"
        
        # Валидация полей и установка дополнений
        self.ui.register_number.setValidator(QIntValidator(self.ui.register_number))
        type_list = ProductDataService.type_list()
        product_completer = QCompleter(type_list, self)
        product_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.ui.product_type.setCompleter(product_completer)

        self.ui.add.clicked.connect(self.confirm_adding)
        self.ui.ok.clicked.connect(self.accept)
        self.ui.cancel.clicked.connect(self.reject)

    def confirm_adding(self):
        """Добавление данных о новой продукции в базу.
        
        Данные собираются с формы диалогового окна и проверяются на заполнение.
        """
        product_id = self.ui.register_number.text()
        product_type = self.ui.product_type.text()
        designation = self.ui.designation.text()

        # Если номер ведомости, тип и описание заполнены, то можно добавлять
        if product_id and product_type and designation:
            success = StandardDataService.save_record(
                'products',
                product_id=product_id,
                product_type=product_type,
                designation=designation
            )
            if success:
                QMessageBox.information(
                    self,
                    f'Продукция {product_id}',
                    f'Продукция с номером ведомости №{product_id}\n'
                    'успешно добавлена!',
                    QMessageBox.Ok
                )
                self.recordSavedSuccess.emit([product_id, product_type, designation])
            else:
                QMessageBox.critical(
                    self,
                    'Ошибка добавления',
                    f'Продукция с номером ведомости №{product_id}\n'
                    'не была добавлена в базу из-за программной ошибки!',
                    QMessageBox.Ok
                )
        else:
            self.timer.start(self.duration)
            self.highlight()

    def highlight(self):
        if not self.ui.register_number.text():
            QToolTip.showText(self.ui.register_number.mapToGlobal(QPoint(0, 0)), self.tip, self.ui.register_number, msecShowTime=self.duration)
            self.ui.register_number.setStyleSheet('QLineEdit {border: 2px solid red; padding-left: -1px;}')
        if not self.ui.product_type.text():
            QToolTip.showText(self.ui.product_type.mapToGlobal(QPoint(0, 0)), self.tip, self.ui.product_type, msecShowTime=self.duration)
            self.ui.product_type.setStyleSheet('QLineEdit {border: 2px solid red; padding-left: -1px;}')
        if not self.ui.designation.text():
            QToolTip.showText(self.ui.designation.mapToGlobal(QPoint(0, 0)), self.tip, self.ui.designation, msecShowTime=self.duration)
            self.ui.designation.setStyleSheet('QLineEdit {border: 2px solid red; padding-left: -1px;}')

    def cooldown(self):
        self.ui.register_number.setStyleSheet('')
        self.ui.product_type.setStyleSheet('')
        self.ui.designation.setStyleSheet('')


class ArticleDialog(QDialog):
    """Диалоговое окно добавления нового изделия.
    
    После добавления нового изделия посылает сигнал с параметрами для того,
    чтобы основное окно каталога обновило данные в модели.
    """

    recordSavedSuccess = Signal(list)

    def __init__(self, parent):
        super(ArticleDialog, self).__init__(parent)
        self.ui = ui_add_article_dialog.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle('Добавление изделия')
        
        # Таймер для подсветки ошибки
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.cooldown)
        self.duration = 1500
        self.tip = "Укажите артикул"

        self.ui.add.clicked.connect(self.confirm_adding)
        self.ui.ok.clicked.connect(self.accept)
        self.ui.cancel.clicked.connect(self.reject)

    def set_title_data(self, v1: str, v2: str, v3: str):
        """Установка данных о продукции.

        :param v1: Номер ведомости
        :type v1: str
        :param v2: Описание продукции
        :type v2: str
        :param v3: Тип продукции
        :type v3: str
        """
        self.ui.register_number.setText(v1)
        self.ui.designation.setText(v2)
        self.ui.product_type.setText(v3)

    def confirm_adding(self):
        """Добавление данных о новом изделии в базу.
        
        Данные собираются с формы диалогового окна и проверяются на заполнение.
        """
        nomenclature = self.ui.nomenclature.text()
        rent = int(self.ui.rent.isChecked())
        product_id = int(self.ui.register_number.text())
        type = self.ui.product_type.text()

        # Если заполнена номенклатура и номер ведомости
        if nomenclature:
            success = StandardDataService.save_record(
                'articles', product_id=product_id, nomenclature=nomenclature, rent=rent
            )
            if success:
                QMessageBox.information(
                    self,
                    f'Продукция {product_id}',
                    f'Изделие {nomenclature}\nуспешно добавлено!',
                    QMessageBox.Ok
                )
                self.recordSavedSuccess.emit([product_id, type, nomenclature, rent])
            else:
                QMessageBox.critical(
                    self,
                    'Ошибка добавления',
                    f'Изделие {nomenclature}\nне было добавлено в базу '
                    'из-за программной ошибки!',
                    QMessageBox.Ok
                )
        else:
            self.timer.start(self.duration)
            self.highlight()

    def highlight(self):
        QToolTip.showText(self.ui.nomenclature.mapToGlobal(QPoint(0, 0)), self.tip, self.ui.nomenclature, msecShowTime=self.duration)
        self.ui.nomenclature.setStyleSheet('QLineEdit {border: 2px solid red; padding-left: -1px;}')

    def cooldown(self):
        self.ui.nomenclature.setStyleSheet('')


class DetailDialog(QDialog):
    """Диалоговое окно добавления новой заготовки.
    
    После добавления новой заготовки посылает сигнал с параметрами для того,
    чтобы основное окно каталога обновило данные в модели.
    """

    recordSavedSuccess = Signal(list)

    def __init__(self, parent):
        super(DetailDialog, self).__init__(parent)
        self.ui = ui_add_detail_dialog.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle('Добавление заготовки')
        
        # Таймер для подсветки ошибки
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.cooldown)
        self.duration = 1500
        self.tip = "Укажите название заготовки"

        # Настройка списка со сплавами
        self.fusions = {}
        for fusion in FusionDataService.fusions_list():
            self.fusions[fusion['name']] = fusion['fusion_id']
        self.ui.fusions.addItems(list(self.fusions.keys()))

        # Настройка списка с направлениями
        self.directions = {}
        for direction in DirectionDataService.directions_list():
            self.directions[direction['name']] = direction['direction_id']
        self.ui.directions.addItems(list(self.directions.keys()))

        self.ui.add.clicked.connect(self.confirm_adding)
        self.ui.ok.clicked.connect(self.accept)
        self.ui.cancel.clicked.connect(self.reject)

    def set_title_data(self, v1: str, v2: str, v3: str):
        """Установка данных о продукции.

        :param v1: Номер ведомости
        :type v1: str
        :param v2: Описание продукции
        :type v2: str
        :param v3: Тип продукции
        :type v3: str
        """
        self.ui.register_number.setText(v1)
        self.ui.designation.setText(v2)
        self.ui.product_type.setText(v3)

    def confirm_adding(self):
        """Добавление данных о новой заготовке в базу.
        
        Данные собираются с формы диалогового окна и проверяются на заполнение.
        """
        name = self.ui.name.text()
        product_id = int(self.ui.register_number.text())
        fusion = self.fusions[self.ui.fusions.currentText()]
        height = self.ui.height.value()
        width = self.ui.width.value()
        depth = self.ui.depth.value()
        direction = self.directions[self.ui.directions.currentText()]
        priority = self.ui.priority.value()
        amount = self.ui.amount.value()

        # Если имя, габаритные размеры и количество заполнены, то добавляем
        if name:
            success = StandardDataService.save_record(
                'details', name=name, product_id=product_id,
                fusion_id=fusion, height=height, width=width, depth=depth,
                amount=amount, priority=priority, direction_id=direction
            )
            if success:
                QMessageBox.information(
                    self,
                    f'Продукция {product_id}',
                    f'Деталь {name}\nуспешно добавлена!',
                    QMessageBox.Ok
                )
                self.recordSavedSuccess.emit([
                    name, self.ui.fusions.currentText(), height, width, depth, amount,
                    priority, self.ui.directions.currentText(), product_id
                ])
            else:
                QMessageBox.critical(
                    self,
                    'Ошибка добавления',
                    f'Деталь {name}\nне была добавлена в базу '
                    'из-за программной ошибки!',
                    QMessageBox.Ok
                )
        else:
            self.timer.start(self.duration)
            self.highlight()

    def highlight(self):
        QToolTip.showText(self.ui.name.mapToGlobal(QPoint(0, 0)), self.tip, self.ui.name, msecShowTime=self.duration)
        self.ui.name.setStyleSheet('QLineEdit {border: 2px solid red; padding-left: -1px;}')

    def cooldown(self):
        self.ui.name.setStyleSheet('')


class OrderAddingDialog(QDialog):
    """Диалоговое окно добавления нового заказа.

    После добавления нового заказа не посылает сигнал с параметрами, т.к.
    главный сценарий использования окна включает добавление одного заказа и
    дальнейшую работу уже с ним, а не создание прочих заказов.
    """

    recordSavedSuccess = Signal(dict)
    predictedIngotSaved = Signal(dict, dict, Tree)

    def __init__(self, parent):
        super(OrderAddingDialog, self).__init__(parent)
        self.ui = ui_add_order_dialog.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.Window)
        self.setWindowState(Qt.WindowMaximized)

        # Иерархическая модель изделие->заготовки для формирования заказа
        # ID (int) - идентификатор конкретного изделия или заготовки
        # ADDED (bool) - статус добавления этой заготовки или изделия в заказ
        self.headers = [
            'Ведомость', 'Название', 'Аренда', 'Сплав', 'Длина', 'Ширина',
            'Толщина', 'Количество', 'Приоритет', 'Направление', 'ID', 'ADDED'
        ]
        self.catalog_headers = self.headers[:3]
        self.added_headers = self.headers[:2] + self.headers[3:9]
        self.model = ComplectsModel(self.headers)
        
        # Модель данных со свободными слитками
        self.ingot_model = IngotModel()
        self.ingot_delegate = IngotSectionDelegate(self.ui.ingotsView)
        self.ui.ingotsView.setModel(self.ingot_model)
        self.ui.ingotsView.setItemDelegate(self.ingot_delegate)

        # Храним данные о расчитанных слитках
        self.predicted_ingots = {}

        # Прокси-модель для поиска нужных изделий (фильтр по названию)
        self.search_proxy = ArticleInformationFilterProxyModel()
        self.search_proxy.setSourceModel(self.model)
        self.ui.treeView_1.setModel(self.search_proxy)

        # Прокси модель добавленных заготовок и изделий (фильтр по флагу ADDED)
        self.choice_proxy = OrderComplectsFilterProxyModel()
        self.choice_proxy.setSourceModel(self.model)
        self.ui.treeView_2.setModel(self.choice_proxy)

        # Назначение меню кнопке
        self.menu = QMenu()
        self.fusions = {}
        for fusion in FusionDataService.fusions_list():
            self.fusions[fusion['name']] = fusion['fusion_id']
            # Под каждый сплав создаётся отдельное событие выпадающего меню
            action: QAction = self.menu.addAction(fusion[1])
            action.setObjectName(fusion['name'])
            action.triggered.connect(self.calculate_ingot)
        self.ui.pushButton.setMenu(self.menu)

        # Выравниваем ширину колонок левого представления под контент
        for column in range(self.model.columnCount(QModelIndex())):
            self.ui.treeView_1.resizeColumnToContents(column)

        # Скрываем ненужные нам колонки в соответствии со списками заголовков
        for index, column in enumerate(self.headers):
            self.ui.treeView_1.setColumnHidden(index, column not in self.catalog_headers)
            self.ui.treeView_2.setColumnHidden(index, column not in self.added_headers)

        # Связываем сигналы и слоты
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.ui.searchName.textChanged.connect(self.search_proxy.nomenclature)
        self.ui.add.clicked.connect(self.confirm_adding)
        self.ui.cancel.clicked.connect(self.reject)

        # Теневой эффект у разделителя окна
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setColor(Qt.gray)
        self.shadow_effect.setYOffset(0)
        self.shadow_effect.setXOffset(6)
        self.shadow_effect.setBlurRadius(13)
        self.ui.splitter.handle(1).setGraphicsEffect(self.shadow_effect)

    def showContextMenu(self, point: QPointF):
        """Метод вызова контекстного меню.

        Отвечает за добавление и удаление заготовок и изделий из комплектации
        заказа (путём изменения флага ADDED у записи или записей).

        :param point: Точка выхова контекстного меню
        :type point: QPointF
        """
        menu = QMenu()
        if self.ui.treeView_1.hasFocus():
            if self.model.rowCount(QModelIndex()):
                if self.ui.treeView_1.currentIndex().parent().isValid():
                    add = menu.addAction('Добавить деталь')
                    add.triggered.connect(self.add_detail_to_complect)
                else:
                    add = menu.addAction('Добавить изделие целиком')
                    add.triggered.connect(self.add_article_to_complect)
        if self.ui.treeView_2.hasFocus():
            if self.model.rowCount(QModelIndex()):
                if self.ui.treeView_2.currentIndex().parent().isValid():
                    delete = menu.addAction('Убрать деталь')
                    delete.triggered.connect(self.remove_detail_from_complect)
                else:
                    delete = menu.addAction('Убрать изделие целиком')
                    delete.triggered.connect(self.remove_article_from_complect)
        menu.exec_(self.mapToGlobal(point))

    def add_article_to_complect(self):
        index = self.search_proxy.mapToSource(self.ui.treeView_1.currentIndex())
        parent = self.model.parent(index)

        # HACK: если не перенести индекс на первую колонку, работать не будет
        index = self.model.index(index.row(), 0, parent)

        parent_state_index = self.model.index(index.row(), 11, parent)
        self.model.setData(parent_state_index, True, Qt.EditRole)

        for row in range(self.model.rowCount(index)):
            child_state_index = self.model.index(row, 11, index)
            self.model.setData(child_state_index, True, Qt.EditRole)

        for column in range(self.model.columnCount(QModelIndex())):
            self.ui.treeView_2.resizeColumnToContents(column)
        # Колонка со сплавами по другому размер не меняет
        self.ui.treeView_2.setColumnWidth(3, 80)

    def add_detail_to_complect(self):
        index = self.search_proxy.mapToSource(self.ui.treeView_1.currentIndex())
        parent = self.model.parent(index)

        # HACK: если не перенести индекс на первую колонку, работать не будет
        index = self.model.index(index.row(), 0, parent)

        child_state_index = self.model.index(index.row(), 11, parent)
        self.model.setData(child_state_index, True, Qt.EditRole)

        parent_state_index = self.model.index(parent.row(), 11, QModelIndex())
        self.model.setData(parent_state_index, True, Qt.EditRole)

        for column in range(self.model.columnCount(QModelIndex())):
            self.ui.treeView_2.resizeColumnToContents(column)
        # Колонка со сплавами по другому размер не меняет
        self.ui.treeView_2.setColumnWidth(3, 80)

    def remove_article_from_complect(self):
        index = self.choice_proxy.mapToSource(self.ui.treeView_2.currentIndex())
        parent = self.model.parent(index)

        # HACK: если не перенести индекс на первую колонку, работать не будет
        index = self.model.index(index.row(), 0, parent)

        parent_state_index = self.model.index(index.row(), 11, parent)
        self.model.setData(parent_state_index, False, Qt.EditRole)

        # Если убирается изделие, то убираются и все его заготовки
        for row in range(self.model.rowCount(index)):
            child_state_index = self.model.index(row, 11, index)
            self.model.setData(child_state_index, False, Qt.EditRole)

    def remove_detail_from_complect(self):
        index = self.choice_proxy.mapToSource(self.ui.treeView_2.currentIndex())
        parent = self.model.parent(index)

        # HACK: если не перенести индекс на первую колонку, работать не будет
        index = self.model.index(index.row(), 0, parent)

        # Если является последней убираемой заготовкой, то убрать и изделие
        child_state_index = self.model.index(index.row(), 11, parent)
        self.model.setData(child_state_index, False, Qt.EditRole)
        if not self.article_have_details(parent):
            row = parent.row()
            parent_state_index = self.model.index(row, 11, QModelIndex())
            self.model.setData(parent_state_index, False, Qt.EditRole)

    def article_have_details(self, index: QModelIndex) -> bool:
        """Проверка наличия другой выбранной заготовки в пределах изделия.

        :param index: Ссылка на проверяемую запись
        :type index: QModelIndex
        :return: Истина, если есть другие заготовки, и ложь в обратном случае
        :rtype: bool
        """
        rows_states = []
        for row in range(self.model.rowCount(index)):
            row_index = self.model.index(row, 11, index)
            rows_states.append(self.model.data(row_index, Qt.DisplayRole))
        return any(rows_states)

    def calculate_ingot(self):
        sender = self.sender()
        
        # По свойству objectName узнаём о выбранном сплаве
        fusion_name = sender.objectName()
        material = Material(fusion_name, 2.2, 1.)

        progress = QProgressDialog('OCI', 'Отмена', 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle('Рассчет слитка под ПЗ')
        progress.forceShow()
        # FIXME: получить имя заказа
        # FIXME: а имени может и не быть, расчёт слитков происходит при добавлении заказа
        order_name = 'ЗАКАЗ'
        progress.setLabelText('Процесс расчета слитка под ПЗ...') 

        if self.choice_proxy.rowCount(QModelIndex()):
            details = self.get_details_kit(material)
            if details.is_empty():
                # TODO: уведомить пользователя о том, что нет таких заготовок
                progress.close()
                return
            logging.info(
                'Попытка расчета слитка под ПЗ %(name)s: '
                '%(blanks)d заготовок, %(heights)d толщин',
                {'name': order_name, 'blanks': details.qty(),
                'heights': len(details.keys())}
            )
            try:
                sizes, tree, efficiency = self.predict_size(
                    material, details, progress=progress
                )
                logging.info(
                    'Расчет слитка %(name)s успешно завершен. '
                    'Размеры: %(length)d, %(width)d, %(height)d; '
                    'эффективность: %(efficiency)d толщин',
                    {'name': order_name, 'length': sizes[0],
                    'width': sizes[1], 'height': sizes[2],
                    'efficiency': efficiency}
                )
            except ForcedTermination:
                logging.info(
                    'Расчет слитка для заказа %(name)s прерван пользователем.',
                    {'name': order_name}
                )
                QMessageBox.information(self, 'Внимание', 'Процесс расчета слитка был прерван!', QMessageBox.Ok)
                return
            progress.close()
            data_row = {
                'ingot_id': 0,
                'fusion_id': self.fusions[fusion_name],
                'ingot_part': None,
                'ingot_size': sizes,
                'status_id': 4
            }
            for row in range(self.ingot_model.rowCount()):
                ingot_index = self.ingot_model.index(row, 0, QModelIndex())
                if ingot_index.data(Qt.DisplayRole)['status_id'] == 1:
                    continue
                if self.fusions[fusion_name] == ingot_index.data(Qt.DisplayRole)['fusion_id']:
                    self.ingot_model.deleteRow(row, QModelIndex())
                    break
            self.ingot_model.appendRow(data_row)
            self.predicted_ingots[self.fusions[fusion_name]] = {'tree': tree.root, 'efficiency': round(efficiency * 100, 2)}
        else:
            QMessageBox.critical(
                self,
                'Ошибка добавления',
                'Должно быть добавлено хотя бы одно изделие!',
                QMessageBox.Ok
            )

    def get_details_kit(self, material: Material) -> Kit:
        details = []
        # Переходим по всем выбранным изделиям
        for row in range(self.choice_proxy.rowCount(QModelIndex())):
            parent_proxy_index = self.choice_proxy.index(row, 0, QModelIndex())
            parent = self.choice_proxy.mapToSource(parent_proxy_index)
            # HACK: без этого работать не будет
            parent = self.model.index(parent.row(), 0, QModelIndex())
            parent_name_index = self.model.index(parent.row(), 1, QModelIndex())
            parent_name = self.model.data(parent_name_index, Qt.DisplayRole)
            # Переходим по всем заготовкам в изделии
            for sub_row in range(self.model.rowCount(parent)):
                detail_fusion = self.model.data(self.model.index(sub_row, 3, parent), Qt.DisplayRole)
                # Если не совпадают сплав заготовки и выбранного слитка - пропускаем
                if detail_fusion != material.name:
                    continue
                # Если заготовка выбрана <ADDED == True>
                id_index = self.model.index(sub_row, 11, parent)
                if self.model.data(id_index, Qt.DisplayRole):
                    name: str = self.model.data(self.model.index(sub_row, 1, parent), Qt.DisplayRole)
                    length = int(self.model.data(self.model.index(sub_row, 4, parent), Qt.DisplayRole))
                    width = int(self.model.data(self.model.index(sub_row, 5, parent), Qt.DisplayRole))
                    depth = float(self.model.data(self.model.index(sub_row, 6, parent), Qt.DisplayRole))
                    sizes: Sizes = [length, width, depth]
                    amount = int(self.model.data(self.model.index(sub_row, 7, parent), Qt.DisplayRole))
                    priority = int(self.model.data(self.model.index(sub_row, 8, parent), Qt.DisplayRole))
                    direction_id = int(self.model.realdata(self.model.index(sub_row, 9, parent), Qt.DisplayRole))
                    direction_code = 3 if direction_id == 1 else 2
                    direction = Direction(direction_code)
                    # Создаём заготовки из полученных данных
                    for _ in range(amount):
                        blank = Blank(*sizes, priority, direction=direction, material=material)
                        blank.name = parent_name + '_' + name
                        details.append(blank)
        kit = Kit(details)
        kit.sort('width')
        return kit

    def predict_size(self, material: Material, kit: Kit, progress=None):
        # TODO: считать из настроек максимальные параметры слитка
        #       без припусков на фрезеровку и погрешность!
        max_size = self.ingot_settings['max_size']
        
        bin_ = Bin(*max_size, material=material)
        root = BinNode(bin_, kit=kit)
        tree = Tree(root)

        # TODO: считать из настроек минимальные параметры слитка
        #       без припусков на фрезеровку и погрешность!
        min_size = self.ingot_settings['min_size']

        # Дерево с рассчитанным слитком
        tree = self.parent().optimal_ingot_size(
            tree, min_size, max_size, self.settings, progress=progress
        )
        efficiency = round(solution_efficiency(tree.root, list(dfs(tree.root)), is_total=True), 2)
        # print(f'Эффективность после расчета: {efficiency}')

        # TODO: Получить из настроек погрешность и припуски на фрезеровку
        size_error = 2
        allowance = 1.5

        # Получение слитка с учетом погрешности и припусков
        length = tree.root.bin.length # + size_error + 2 * allowance
        width = tree.root.bin.width # + size_error + 2 * allowance
        height = tree.root.bin.height # + size_error + 2 * allowance

        # print(f'Финальные размеры: {length, width, height}')
        # print(f'Масса слитка (в гр): {length * width * height * material.density / 1000}')
        # print(f'Масса слитка (в кг): {length * width * height * material.density / 1_000_000}')
        # print(f'{material.density = }')
        return [math.ceil(length), math.ceil(width), math.ceil(height)], tree, efficiency

    def repeatable_fusions(self, indexes: List[QModelIndex]):
        fusions_id = []
        for index in indexes:
            ingot = index.data(Qt.DisplayRole)
            if ingot['fusion_id'] in fusions_id:
                return True
            fusions_id.append(ingot['fusion_id'])
        return False

    def confirm_adding(self):
        """Добавление данных о новом заказе в базу.
        
        Данные собираются с формы диалогового окна и проверяются на заполнение.
        """
        # Имя и статус складирования заказа - основа записи в базе данных
        order_name = self.ui.orderName.text()
        selected_indexes = self.ui.ingotsView.selectedIndexes()

        if self.repeatable_fusions(selected_indexes):
            QMessageBox.critical(
                self,
                'Ошибка добавления',
                f'Выбраны слитки одинаковых сплавов.',
                QMessageBox.Ok
            )
            return

        # Если заполнено имя, выбран хотя бы один слиток и изделие
        if order_name and selected_indexes and self.choice_proxy.rowCount(QModelIndex()):
            creation_date = datetime.today().strftime("%d_%m_%Y")
            success = StandardDataService.save_record(
                'orders',
                status_id=1,
                name=order_name,
                date=creation_date
            )
            if success:
                order_id = OrderDataService.max_id()
                used_fusions = []
                planned_status = False
                # Проходим по всем выбранным слиткам
                for index in selected_indexes:
                    current_ingot = self.ingot_model.data(index, Qt.DisplayRole)
                    # Если текущий слиток <эфемерный>, то добавляем в базу
                    if current_ingot['status_id'] == 4:
                        predicted_tree = self.predicted_ingots[current_ingot['fusion_id']]['tree']
                        predicted_efficiency = self.predicted_ingots[current_ingot['fusion_id']]['efficiency']
                        current_ingot['ingot_id'] = StandardDataService.save_record(
                            'ingots',
                            fusion_id=current_ingot['fusion_id'],
                            height=current_ingot['ingot_size'][0],
                            width=current_ingot['ingot_size'][1],
                            depth=current_ingot['ingot_size'][2],
                            order_id=order_id,
                            status_id=3,
                            efficiency=predicted_efficiency
                        )
                        self.predictedIngotSaved.emit({'order_id': order_id, 'creation_date': creation_date}, current_ingot, predicted_tree)
                        planned_status = True
                    # Если текущий слиток <слиток>, то обновляем связку
                    else:
                        StandardDataService.update_record(
                            'ingots',
                            {'ingot_id': current_ingot['ingot_id']},
                            order_id=order_id
                        )
                    used_fusions.append(current_ingot['fusion_id'])

                # Добавляем записи о комплектации заказа в целом
                for row in range(self.choice_proxy.rowCount(QModelIndex())):
                    parent_proxy_index = self.choice_proxy.index(row, 0, QModelIndex())
                    parent = self.choice_proxy.mapToSource(parent_proxy_index)

                    # HACK: без этого работать не будет
                    parent = self.model.index(parent.row(), 0, QModelIndex())

                    article_id_index = self.model.index(parent.row(), 10, QModelIndex())
                    article_id = self.model.data(article_id_index, Qt.DisplayRole)

                    # Добавляем записи о заготовках в заказе
                    for sub_row in range(self.model.rowCount(parent)):
                        added_index = self.model.index(sub_row, 11, parent)

                        if not self.model.data(added_index, Qt.DisplayRole):
                            continue
                        amount_index = self.model.index(sub_row, 7, parent)
                        amount = int(self.model.data(amount_index, Qt.DisplayRole))
                        priority_index = self.model.index(sub_row, 8, parent)
                        priority = int(self.model.data(priority_index, Qt.DisplayRole))
                        detail_id_index = self.model.index(sub_row, 10, parent)
                        detail_id = int(self.model.data(detail_id_index, Qt.DisplayRole))
                        fusion_id_index = self.model.index(sub_row, 3, parent)
                        fusion_id = int(self.model.realdata(fusion_id_index, Qt.DisplayRole))
                        status_id = 1 if fusion_id in used_fusions else 6
                        StandardDataService.save_record(
                            'complects',
                            order_id=order_id,
                            article_id=article_id,
                            detail_id=detail_id,
                            amount=amount,
                            priority=priority,
                            status_id=status_id
                        )
                QMessageBox.information(
                    self,
                    'Добавление заказа',
                    f'Заказ {order_name} был успешно добавлен в базу!',
                    QMessageBox.Ok
                )
                if planned_status:
                    StandardDataService.update_record(
                        'orders',
                        {'order_id': order_id},
                        status_id=6,
                        efficiency=OrderDataService.efficiency({'order_id': order_id})
                    )
                pack = {
                    'order_id': order_id,
                    'status_id': 6 if planned_status else 1,
                    'order_name': order_name,
                    'current_depth': 0.0,
                    'efficiency': OrderDataService.efficiency({'order_id': order_id}),
                    'creation_date': datetime.today().strftime("%d_%m_%Y")
                }
                self.recordSavedSuccess.emit(pack)
                logging.info('Заказ %(name)s добавлен в базу.', {'name': order_name})
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    'Ошибка добавления',
                    f'Заказ {order_name} не был добавлен в базу!',
                    QMessageBox.Ok
                )
        else:
            QMessageBox.critical(
                self,
                'Ошибка добавления',
                'Поле названия заказа обязательно должно быть заполнено!\n'
                'Должен быть выбран хотя бы один слиток!\n'
                'Должно быть добавлено хотя бы одно изделие!',
                QMessageBox.Ok
            )

    def set_settings(self, settings: Dict, ingot_settings: Dict):
        self.settings = settings
        self.ingot_settings = ingot_settings


class IngotAddingDialog(QDialog):

    def __init__(self, parent=None):
        super(IngotAddingDialog, self).__init__(parent)
        self.ui = ui_add_ingot_dialog.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle('Добавление слитка')

        # Таймер для подсветки ошибки
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.cooldown)
        self.duration = 1500
        self.tip = 'Укажите название партии'

        # Настройка списка со сплавами
        self.fusions = {}
        for fusion in FusionDataService.fusions_list():
            self.fusions[fusion['name']] = fusion['fusion_id']
        self.ui.fusion.addItems(list(self.fusions.keys()))

        self.ui.add.clicked.connect(self.confirm_adding)
        self.ui.cancel.clicked.connect(self.reject)

    def confirm_adding(self):
        batch = self.ui.batch.text()
        height = self.ui.height.value()
        width = self.ui.width.value()
        depth = self.ui.depth.value()
        fusion = self.fusions[self.ui.fusion.currentText()]

        if batch and height and width and depth:
            success = StandardDataService.save_record(
                'ingots',
                fusion_id=fusion,
                batch=batch,
                height=height,
                width=width,
                depth=depth
            )
            if success:
                QMessageBox.information(
                    self,
                    f'Партия {batch}',
                    f'Слиток из партии {batch}\nуспешно добавлен!',
                    QMessageBox.Ok
                )
            else:
                QMessageBox.critical(
                    self,
                    'Ошибка добавления',
                    f'Слиток из партии {batch} не был добавлен в базу\n'
                    'из-за программной ошибки!',
                    QMessageBox.Ok
                )
        else:
            self.timer.start(self.duration)
            self.highlight()

    def highlight(self):
        QToolTip.showText(self.ui.batch.mapToGlobal(QPoint(0, 0)), self.tip, self.ui.batch, msecShowTime=self.duration)
        self.ui.batch.setStyleSheet('QLineEdit {border: 2px solid red; padding-left: -1px;}')

    def cooldown(self):
        self.ui.batch.setStyleSheet('')


class IngotReadinessDialog(QDialog):

    def __init__(self, parent: typing.Optional[QWidget]) -> None:
        super(IngotReadinessDialog, self).__init__(parent)
        self.ui = ui_ready_ingot_dialog.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle('Подтверждение готовности')

        # Таймер для подсветки ошибки
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.cooldown)
        self.duration = 1500
        self.tip = 'Укажите название партии'

        self.ui.add.clicked.connect(self.confirm_readiness)
        self.ui.cancel.clicked.connect(self.reject)

    def set_title_data(self, id: int, sizes: List, fusion: str):
        self.id = id
        self.ui.height_label.setText(str(sizes[0]))
        self.ui.width_label.setText(str(sizes[1]))
        self.ui.depth_label.setText(str(sizes[2]))
        self.ui.fusion_label.setText(fusion)
    
    def get_batch(self):
        return self.ui.batch.text()

    def confirm_readiness(self):
        batch = self.ui.batch.text()
        if batch:
            success = StandardDataService.update_record(
                'ingots',
                {'ingot_id': self.id},
                status_id=1,
                batch=batch
            )
            if success:
                QMessageBox.information(
                    self,
                    f'Партия {batch}',
                    f'Слиток из партии {batch}\nуспешно добавлен!',
                    QMessageBox.Ok
                )
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    'Ошибка добавления',
                    f'Слиток из партии {batch} не был добавлен в базу.',
                    QMessageBox.Ok
                )
        else:
            self.timer.start(self.duration)
            self.highlight()

    def highlight(self):
        QToolTip.showText(self.ui.batch.mapToGlobal(QPoint(0, 0)), self.tip, self.ui.batch, msecShowTime=self.duration)
        self.ui.batch.setStyleSheet('QLineEdit {border: 2px solid red; padding-left: -1px;}')

    def cooldown(self):
        self.ui.batch.setStyleSheet('')


class FullScreenWindow(QDialog):
    def __init__(self, parent: QWidget = None):
        super(FullScreenWindow, self).__init__(parent)
        self.ui = ui_full_screen.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle('Карта: полноэкранный режим')

    def set_scene(self, scene: QGraphicsScene):
        self.ui.graphicsView.setScene(scene)
