import math
import logging
import typing
from datetime import datetime
from typing import Dict, Tuple, Union, Optional
from collections import Counter

from PyQt5.QtCore import (
    QItemSelectionModel, QPoint, QTimer, Qt, pyqtSignal, QPointF, QModelIndex, QObject
)
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (
    QDialog, QGraphicsScene, QMessageBox, QMenu, QPushButton, QToolTip, QWidget,
    QProgressDialog, QAction
)

from sequential_mh.bpp_dsc.rectangle import Material, Kit, Bin
from sequential_mh.bpp_dsc.tree import (
    BinNode, Tree, solution_efficiency
)
from sequential_mh.bpp_dsc.support import dfs
from gui import (
    ui_add_article_dialog, ui_add_detail_dialog,
    ui_add_order_dialog, ui_add_ingot_dialog, ui_full_screen,
    ui_ready_ingot_dialog, ui_assign_ingot_dialog, ui_edit_order_dialog,
    ui_finish_step_dialog
)
from service import (
    OrderDataService, StandardDataService, CatalogDataService, Field, FieldCollection
)
from models import (
   OrderComplectsFilterProxyModel, ComplectsModel, IngotModel, 
   CatalogFilterProxyModel, OrderInformationComplectsModel, ResidualsModel
)
from widgets import (
    IngotSectionDelegate,
    ListValuesDelegate,
    ResidualsSectionDelegate
)
from exceptions import ForcedTermination
from log import log_operation_info


Number = Union[int, float]
Sizes = Tuple[Number, Number, Number]


class ArticleDialog(QDialog):
    """Диалоговое окно добавления новой продукции.

    После добавления новой продукции посылает сигнал с параметрами для того,
    чтобы основное окно каталога обновило данные в модели.
    """

    recordSavedSuccess = pyqtSignal(list)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.ui = ui_add_article_dialog.Ui_Dialog()
        self.ui.setupUi(self)

        # Таймер для подсветки ошибки
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.cooldown)

        # Валидация полей и установка дополнений
        self.ui.regnum.setValidator(QIntValidator(self.ui.regnum))

        self.ui.add.clicked.connect(self.confirm_adding)

    def confirm_adding(self):
        """Добавление данных о новой продукции в базу.

        Данные собираются с формы диалогового окна и проверяются на заполнение.
        """
        id_ = self.ui.regnum.text()
        name = self.ui.name.text()

        # Если номер ведомости, тип и описание заполнены, то можно добавлять
        if not id_ or not name:
            self.timer.start(1500)
            self.highlight()
            return

        id_ = StandardDataService.save_record('articles', id=id_, name=name)
        if not id_:
            QMessageBox.critical(self, 'Ошибка добавления', 'Изделие не было добавлено в базу!', QMessageBox.Ok)
            return

        QMessageBox.information(self, f'Изделие {id_}', f'Изделие №{id_} успешно добавлено!', QMessageBox.Ok)
        self.recordSavedSuccess.emit([id_, name])

    def highlight(self):
        if not self.ui.regnum.text():
            QToolTip.showText(self.ui.regnum.mapToGlobal(QPoint(0, 0)), "Поле необходимо заполнить", self.ui.regnum)
            self.ui.regnum.setStyleSheet('QLineEdit {border: 2px solid red; padding-left: -1px;}')
        if not self.ui.name.text():
            QToolTip.showText(self.ui.name.mapToGlobal(QPoint(0, 0)), "Поле необходимо заполнить", self.ui.name)
            self.ui.name.setStyleSheet('QLineEdit {border: 2px solid red; padding-left: -1px;}')

    def cooldown(self):
        self.ui.regnum.setStyleSheet('')
        self.ui.name.setStyleSheet('')


class DetailDialog(QDialog):
    """Диалоговое окно добавления новой заготовки.

    После добавления новой заготовки посылает сигнал с параметрами для того,
    чтобы основное окно каталога обновило данные в модели.
    """

    recordSavedSuccess = pyqtSignal(list)

    def __init__(self, name: str, id_: int, parent: Optional[QObject] = None):
        super(DetailDialog, self).__init__(parent)
        self.ui = ui_add_detail_dialog.Ui_Dialog()
        self.ui.setupUi(self)

        # Идентификатор изделия, к которому привязываются заготовки
        self.article_id = id_

        # Таймер для подсветки ошибки
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.cooldown)

        # Настройка списка с направлениями
        self.directions_list = CatalogDataService.directions_list()
        self.ui.direction.addItems(list(self.directions_list.keys()))

        # Настройка списка со сплавами
        self.fusions_list = CatalogDataService.fusions_list()
        self.ui.fusion.addItems(list(self.fusions_list.keys()))

        self.ui.add.clicked.connect(self.confirm_adding)

    def confirm_adding(self):
        name = self.ui.name.text()
        article_id = self.article_id
        fusion_id = self.fusions_list[self.ui.fusion.currentText()]
        direction_id = self.directions_list[self.ui.direction.currentText()]
        l = self.ui.length.value()
        w = self.ui.width.value()
        h = self.ui.heigth.value()
        amount = self.ui.amount.value()
        priority = self.ui.priority.value()

        # Если имя заполнено, то добавляем
        if not name:
            self.timer.start(1500)
            self.highlight()
            return

        detail_id = StandardDataService.save_record(
            'details', name=name, article_id=article_id, fusion_id=fusion_id, 
            direction_id=direction_id, length=l, width=w, height=h,
            amount=amount, priority=priority
        )

        if not detail_id:
            QMessageBox.critical(self, 'Ошибка добавления', f'Деталь {name}не была добавлена в базу!', QMessageBox.Ok)
            return

        QMessageBox.information(self, f'Изделие {article_id}', f'Деталь "{name}" успешно добавлена!', QMessageBox.Ok)
        self.recordSavedSuccess.emit([name, fusion_id, l, w, h, amount, priority, direction_id, detail_id])

    def highlight(self):
        QToolTip.showText(self.ui.name.mapToGlobal(QPoint(0, 0)), "Укажите название заготовки", self.ui.name)
        self.ui.name.setStyleSheet('QLineEdit {border: 2px solid red; padding-left: -1px;}')

    def cooldown(self):
        self.ui.name.setStyleSheet('')


class OrderAddingDialog(QDialog):
    """Диалоговое окно добавления нового заказа.

    После добавления нового заказа не посылает сигнал с параметрами, т.к.
    главный сценарий использования окна включает добавление одного заказа и
    дальнейшую работу уже с ним, а не создание прочих заказов.
    """

    recordSavedSuccess = pyqtSignal(dict)

    def __init__(self, parent):
        super().__init__(parent)
        self.ui = ui_add_order_dialog.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.Window)
        self.setWindowState(Qt.WindowMaximized)

        self.ui.name.setText(datetime.now().strftime("%d.%m.%Y %H:%M:%S"))

        # Иерархическая модель изделие->заготовки для формирования заказа
        # ID (int) - идентификатор конкретного изделия или заготовки
        # ADDED (bool) - статус добавления этой заготовки или изделия в заказ
        self.headers = [
            'Ведомость', 'Название', 'Сплав', 'Длина', 'Ширина', 'Толщина',
            'Количество', 'Приоритет', 'Направление', 'Идентификатор', 'Добавлено'
        ]
        self.catalog_headers = self.headers[:3]
        self.added_headers = self.headers[:9]
        self.model = ComplectsModel(self.headers)

        self.fusions = CatalogDataService.fusions_list()
        self.directions = CatalogDataService.directions_list()

        # Прокси-модель для поиска нужных изделий (фильтр по названию)
        self.search_proxy = CatalogFilterProxyModel()
        self.search_proxy.setSourceModel(self.model)
        self.ui.catalog_view.setModel(self.search_proxy)

        # Прокси модель добавленных заготовок и изделий (фильтр по флагу ADDED)
        self.choice_proxy = OrderComplectsFilterProxyModel()
        self.choice_proxy.setSourceModel(self.model)
        self.ui.complects_view.setModel(self.choice_proxy)

        # Выравниваем ширину колонок левого представления под контент
        for column in range(self.model.columnCount(QModelIndex())):
            self.ui.catalog_view.resizeColumnToContents(column)

        self.fusions_delegate = ListValuesDelegate(self.fusions)
        self.directions_delegate = ListValuesDelegate(self.directions)
        self.ui.catalog_view.setItemDelegateForColumn(2, self.fusions_delegate)
        self.ui.complects_view.setItemDelegateForColumn(2, self.fusions_delegate)
        self.ui.complects_view.setItemDelegateForColumn(8, self.directions_delegate)

        # Скрываем ненужные нам колонки в соответствии со списками заголовков
        for index, column in enumerate(self.headers):
            self.ui.catalog_view.setColumnHidden(index, column not in self.catalog_headers)
            self.ui.complects_view.setColumnHidden(index, column not in self.added_headers)

        # Связываем сигналы и слоты
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.ui.catalog_view.doubleClicked.connect(self.add_entity_filter)
        self.ui.complects_view.doubleClicked.connect(self.remove_entity_filter)
        self.ui.search.textChanged.connect(self.search_proxy.name)
        self.ui.add.clicked.connect(self.confirm_adding)

    def show_context_menu(self, point: QPointF):
        """Метод вызова контекстного меню.

        Отвечает за добавление и удаление заготовок и изделий из комплектации
        заказа (путём изменения флага ADDED у записи или записей).

        :param point: Точка вызова контекстного меню
        :type point: QPointF
        """
        menu = QMenu()
        if self.ui.catalog_view.hasFocus():
            if self.model.rowCount(QModelIndex()):
                if self.ui.catalog_view.currentIndex().parent().isValid():
                    add = menu.addAction('Добавить заготовку')
                    add.triggered.connect(self.add_detail_to_complect)
                else:
                    add = menu.addAction('Добавить изделие целиком')
                    add.triggered.connect(self.add_article_to_complect)
        if self.ui.complects_view.hasFocus():
            if self.model.rowCount(QModelIndex()):
                if self.ui.complects_view.currentIndex().parent().isValid():
                    delete = menu.addAction('Убрать заготовку')
                    delete.triggered.connect(self.remove_detail_from_complect)
                else:
                    delete = menu.addAction('Убрать изделие целиком')
                    delete.triggered.connect(self.remove_article_from_complect)
        menu.exec_(self.mapToGlobal(point))

    def add_entity_filter(self, index: QModelIndex):
        if index.column() in [7, 6]:
            return
        if index.parent().isValid():
            self.add_detail_to_complect()
        else:
            self.add_article_to_complect()

    def add_article_to_complect(self):
        index = self.search_proxy.mapToSource(self.ui.catalog_view.currentIndex())
        parent = self.model.parent(index)

        # HACK: если не перенести индекс на первую колонку, работать не будет
        index = self.model.index(index.row(), 0, parent)

        parent_state_index = self.model.index(index.row(), 10, parent)
        self.model.setData(parent_state_index, True, Qt.EditRole)

        for row in range(self.model.rowCount(index)):
            child_state_index = self.model.index(row, 10, index)
            self.model.setData(child_state_index, True, Qt.EditRole)

        for column in range(self.model.columnCount(QModelIndex())):
            self.ui.complects_view.resizeColumnToContents(column)
        self.ui.complects_view.setColumnWidth(1, 210)
        self.ui.complects_view.setColumnWidth(2, 120)
        self.ui.complects_view.expandAll()

    def add_detail_to_complect(self):
        index = self.search_proxy.mapToSource(self.ui.catalog_view.currentIndex())
        parent = self.model.parent(index)

        # HACK: если не перенести индекс на первую колонку, работать не будет
        index = self.model.index(index.row(), 0, parent)

        child_state_index = self.model.index(index.row(), 10, parent)
        self.model.setData(child_state_index, True, Qt.EditRole)

        parent_state_index = self.model.index(parent.row(), 10, QModelIndex())
        self.model.setData(parent_state_index, True, Qt.EditRole)

        for column in range(self.model.columnCount(QModelIndex())):
            self.ui.complects_view.resizeColumnToContents(column)
        self.ui.complects_view.setColumnWidth(1, 210)
        self.ui.complects_view.setColumnWidth(2, 120)
        self.ui.complects_view.expandAll()

    def remove_entity_filter(self, index: QModelIndex):
        if index.column() in [7, 6]:
            return
        if index.parent().isValid():
            self.remove_detail_from_complect()
        else:
            self.remove_article_from_complect()

    def remove_article_from_complect(self):
        index = self.choice_proxy.mapToSource(self.ui.complects_view.currentIndex())
        parent = self.model.parent(index)

        # HACK: если не перенести индекс на первую колонку, работать не будет
        index = self.model.index(index.row(), 0, parent)

        parent_state_index = self.model.index(index.row(), 10, parent)
        self.model.setData(parent_state_index, False, Qt.EditRole)

        # Если убирается изделие, то убираются и все его заготовки
        for row in range(self.model.rowCount(index)):
            child_state_index = self.model.index(row, 10, index)
            self.model.setData(child_state_index, False, Qt.EditRole)

    def remove_detail_from_complect(self):
        index = self.choice_proxy.mapToSource(self.ui.complects_view.currentIndex())
        parent = self.model.parent(index)

        # HACK: если не перенести индекс на первую колонку, работать не будет
        index = self.model.index(index.row(), 0, parent)

        # Если является последней убираемой заготовкой, то убрать и изделие
        child_state_index = self.model.index(index.row(), 10, parent)
        self.model.setData(child_state_index, False, Qt.EditRole)
        if not self.article_have_details(parent):
            row = parent.row()
            parent_state_index = self.model.index(row, 10, QModelIndex())
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
            row_index = self.model.index(row, 10, index)
            rows_states.append(self.model.data(row_index, Qt.DisplayRole))
        return any(rows_states)

    def confirm_adding(self):
        """Добавление данных о новом заказе в базу.

        Данные собираются с формы диалогового окна и проверяются на заполнение.
        """
        # Имя и статус складирования заказа - основа записи в базе данных
        order_name = self.ui.name.text()

        # Если заполнено имя и выбраны изделия
        if not order_name or not self.choice_proxy.rowCount(QModelIndex()):
            QMessageBox.critical(
                self, 'Ошибка добавления',
                'Поле названия заказа обязательно должно быть заполнено!\n'
                'Должно быть добавлено хотя бы одно изделие!', QMessageBox.Ok
            )
            return

        creation_date = datetime.today().strftime("%d_%m_%Y")
        order_id = StandardDataService.save_record('orders', status_id=0, name=order_name, date=creation_date)

        if not order_id:
            QMessageBox.critical(self, 'Ошибка добавления', f'Заказ {order_name} не был добавлен в базу!', QMessageBox.Ok)
            return

        # Добавляем записи о комплектации заказа в целом
        marked_rows = self.model.added()
        complects = marked_rows['complects']
        updates = FieldCollection(['order_id', 'article_id', 'detail_id', 'status_id', 'amount', 'priority'])
        order = Field('order_id', order_id)
        status = Field('status_id', 0)
        for article, details in complects.items():
            article = Field('article_id', article)
            for detail in details:
                updates.append(order, article, Field('detail_id', detail[0]), status, Field('amount', detail[1]), Field('priority', detail[2]))
        OrderDataService.save_complects(updates)

        self.recordSavedSuccess.emit({
            'id': order_id,
            'status_id': 0,
            'name': order_name,
            'step': 0.0,
            'efficiency': 0.0,
            'date': creation_date,
            'articles': marked_rows['articles_count'],
            'details': marked_rows['details_count'],
        })
        logging.info('Заказ %(name)s добавлен в базу.', {'name': order_name})
        self.accept()


class OrderEditingDialog(QDialog):

    orderEditedSuccess = pyqtSignal(dict)

    def __init__(self, order: dict, complect: OrderInformationComplectsModel, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.ui = ui_edit_order_dialog.Ui_Dialog()
        self.ui.setupUi(self)

        self.order = order

        # Иерархическая модель изделие->заготовки для формирования заказа
        # ID (int) - идентификатор конкретного изделия или заготовки
        # ADDED (bool) - статус добавления этой заготовки или изделия в заказ
        self.headers = [
            'Ведомость', 'Название', 'Сплав', 'Длина', 'Ширина', 'Толщина',
            'Количество', 'Приоритет', 'Направление', 'Идентификатор', 'Добавлено'
        ]
        self.catalog_headers = self.headers[:3]
        self.added_headers = self.headers[:9]
        self.model = ComplectsModel(self.headers)
        self.restore_state(complect)

        self.fusions = CatalogDataService.fusions_list()
        self.directions = CatalogDataService.directions_list()

        # Прокси-модель для поиска нужных изделий (фильтр по названию)
        self.search_proxy = CatalogFilterProxyModel()
        self.search_proxy.setSourceModel(self.model)
        self.ui.catalog_view.setModel(self.search_proxy)

        # Прокси модель добавленных заготовок и изделий (фильтр по флагу ADDED)
        self.choice_proxy = OrderComplectsFilterProxyModel()
        self.choice_proxy.setSourceModel(self.model)
        self.ui.complects_view.setModel(self.choice_proxy)

        # Выравниваем ширину колонок левого представления под контент
        for column in range(self.model.columnCount(QModelIndex())):
            self.ui.catalog_view.resizeColumnToContents(column)

        self.fusions_delegate = ListValuesDelegate(self.fusions)
        self.directions_delegate = ListValuesDelegate(self.directions)
        self.ui.catalog_view.setItemDelegateForColumn(2, self.fusions_delegate)
        self.ui.complects_view.setItemDelegateForColumn(2, self.fusions_delegate)
        self.ui.complects_view.setItemDelegateForColumn(8, self.directions_delegate)

        # Скрываем ненужные нам колонки в соответствии со списками заголовков
        for index, column in enumerate(self.headers):
            self.ui.catalog_view.setColumnHidden(index, column not in self.catalog_headers)
            self.ui.complects_view.setColumnHidden(index, column not in self.added_headers)
        for column in range(self.model.columnCount(QModelIndex())):
            self.ui.complects_view.resizeColumnToContents(column)
        self.ui.complects_view.setColumnWidth(1, 210)
        self.ui.complects_view.setColumnWidth(2, 120)
        self.ui.complects_view.expandAll()

        # Связываем сигналы и слоты
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.ui.search.textChanged.connect(self.search_proxy.name)
        self.ui.catalog_view.doubleClicked.connect(self.add_entity_filter)
        self.ui.complects_view.doubleClicked.connect(self.remove_entity_filter)
        self.ui.save.clicked.connect(self.confirm_order_editing)

    def show_context_menu(self, point: QPointF):
        """Метод вызова контекстного меню.

        Отвечает за добавление и удаление заготовок и изделий из комплектации
        заказа (путём изменения флага ADDED у записи или записей).

        :param point: Точка вызова контекстного меню
        :type point: QPointF
        """
        menu = QMenu()
        if self.ui.catalog_view.hasFocus():
            if self.model.rowCount(QModelIndex()):
                if self.ui.catalog_view.currentIndex().parent().isValid():
                    add = menu.addAction('Добавить заготовку')
                    add.triggered.connect(self.add_detail_to_complect)
                else:
                    add = menu.addAction('Добавить изделие целиком')
                    add.triggered.connect(self.add_article_to_complect)
        if self.ui.complects_view.hasFocus():
            if self.model.rowCount(QModelIndex()):
                if self.ui.complects_view.currentIndex().parent().isValid():
                    delete = menu.addAction('Убрать заготовку')
                    delete.triggered.connect(self.remove_detail_from_complect)
                else:
                    delete = menu.addAction('Убрать изделие целиком')
                    delete.triggered.connect(self.remove_article_from_complect)
        menu.exec_(self.mapToGlobal(point))

    def add_entity_filter(self, index: QModelIndex):
        if index.column() in [7, 6]:
            return
        if index.parent().isValid():
            self.add_detail_to_complect()
        else:
            self.add_article_to_complect()

    def add_article_to_complect(self):
        index = self.search_proxy.mapToSource(self.ui.catalog_view.currentIndex())
        parent = self.model.parent(index)

        # HACK: если не перенести индекс на первую колонку, работать не будет
        index = self.model.index(index.row(), 0, parent)

        parent_state_index = self.model.index(index.row(), 10, parent)
        self.model.setData(parent_state_index, True, Qt.EditRole)

        for row in range(self.model.rowCount(index)):
            child_state_index = self.model.index(row, 10, index)
            self.model.setData(child_state_index, True, Qt.EditRole)

        for column in range(self.model.columnCount(QModelIndex())):
            self.ui.complects_view.resizeColumnToContents(column)
        self.ui.complects_view.setColumnWidth(1, 210)
        self.ui.complects_view.setColumnWidth(2, 120)
        self.ui.complects_view.expandAll()

    def add_detail_to_complect(self):
        index = self.search_proxy.mapToSource(self.ui.catalog_view.currentIndex())
        parent = self.model.parent(index)

        # HACK: если не перенести индекс на первую колонку, работать не будет
        index = self.model.index(index.row(), 0, parent)

        child_state_index = self.model.index(index.row(), 10, parent)
        self.model.setData(child_state_index, True, Qt.EditRole)

        parent_state_index = self.model.index(parent.row(), 10, QModelIndex())
        self.model.setData(parent_state_index, True, Qt.EditRole)

        for column in range(self.model.columnCount(QModelIndex())):
            self.ui.complects_view.resizeColumnToContents(column)
        self.ui.complects_view.setColumnWidth(1, 210)
        self.ui.complects_view.setColumnWidth(2, 120)
        self.ui.complects_view.expandAll()

    def remove_entity_filter(self, index: QModelIndex):
        if index.column() in [7, 6]:
            return
        if index.parent().isValid():
            self.remove_detail_from_complect()
        else:
            self.remove_article_from_complect()

    def remove_article_from_complect(self):
        index = self.choice_proxy.mapToSource(self.ui.complects_view.currentIndex())
        parent = self.model.parent(index)

        # HACK: если не перенести индекс на первую колонку, работать не будет
        index = self.model.index(index.row(), 0, parent)

        parent_state_index = self.model.index(index.row(), 10, parent)
        self.model.setData(parent_state_index, False, Qt.EditRole)

        # Если убирается изделие, то убираются и все его заготовки
        for row in range(self.model.rowCount(index)):
            child_state_index = self.model.index(row, 10, index)
            self.model.setData(child_state_index, False, Qt.EditRole)

    def remove_detail_from_complect(self):
        index = self.choice_proxy.mapToSource(self.ui.complects_view.currentIndex())
        parent = self.model.parent(index)

        # HACK: если не перенести индекс на первую колонку, работать не будет
        index = self.model.index(index.row(), 0, parent)

        # Если является последней убираемой заготовкой, то убрать и изделие
        child_state_index = self.model.index(index.row(), 10, parent)
        self.model.setData(child_state_index, False, Qt.EditRole)
        if not self.article_have_details(parent):
            row = parent.row()
            parent_state_index = self.model.index(row, 10, QModelIndex())
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
            row_index = self.model.index(row, 10, index)
            rows_states.append(self.model.data(row_index, Qt.DisplayRole))
        return any(rows_states)

    def restore_state(self, model: OrderInformationComplectsModel):
        articles = {}
        details_data = {}
        for row in range(model.rowCount(QModelIndex())):
            article_index = model.index(row, 1, QModelIndex())
            article_id = model.data(article_index, Qt.DisplayRole)
            details = []

            hack_index = model.index(row, 0, QModelIndex())

            for sub_row in range(model.rowCount(article_index)):
                detail_index = model.index(sub_row, 1, hack_index)
                detail_id = model.data(detail_index, Qt.DisplayRole)
                amount_index = model.index(sub_row, 7, hack_index)
                amount = model.data(amount_index, Qt.DisplayRole)
                priority_index = model.index(sub_row, 9, hack_index)
                priority = model.data(priority_index, Qt.DisplayRole)
                details.append(detail_id)
                details_data[detail_id] = (amount, priority)
            articles[article_id] = details
        for row in range(self.model.rowCount(QModelIndex())):
            article_index = self.model.index(row, 0, QModelIndex())
            article_id = self.model.data(article_index, Qt.DisplayRole)
            if article_id in articles:
                added_index = self.model.index(row, 10, QModelIndex())
                self.model.setData(added_index, True, Qt.EditRole)
            else:
                continue
            for sub_row in range(self.model.rowCount(article_index)):
                detail_index = self.model.index(sub_row, 9, article_index)
                detail_id = self.model.data(detail_index, Qt.DisplayRole)
                if detail_id in articles[article_id]:
                    added_index = self.model.index(sub_row, 10, article_index)
                    self.model.setData(added_index, True, Qt.EditRole)
                    amount_index = self.model.index(sub_row, 6, article_index)
                    self.model.setData(amount_index, details_data[detail_id][0], Qt.EditRole)
                    priority_index = self.model.index(sub_row, 7, article_index)
                    self.model.setData(priority_index, details_data[detail_id][1], Qt.EditRole)

    def confirm_order_editing(self):
        if not self.choice_proxy.rowCount(QModelIndex()):
            QMessageBox.critical(self, 'Ошибка изменения','Должно быть добавлено хотя бы одно изделие!', QMessageBox.Ok)
            return

        StandardDataService.delete_by_fields('complects', order_id=self.order['id'])

        # Добавляем записи о комплектации заказа в целом
        marked_rows = self.model.added()
        complects = marked_rows['complects']
        updates = FieldCollection(['order_id', 'article_id', 'detail_id', 'status_id', 'amount', 'priority'])
        order = Field('order_id', self.order['id'])
        status = Field('status_id', 0)
        for article, details in complects.items():
            article = Field('article_id', article)
            for detail in details:
                updates.append(order, article, Field('detail_id', detail[0]), status, Field('amount', detail[1]), Field('priority', detail[2]))
        OrderDataService.save_complects(updates)

        self.orderEditedSuccess.emit({
            'articles': marked_rows['articles_count'],
            'details': marked_rows['details_count'],
        })
        logging.info('Заказ %(name)s обновлён в базе.', {'name': self.order['id']})
        self.accept()


class OrderCompletingDialog(QDialog):
    
    def __init__(self, residuals: list, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.ui = ui_finish_step_dialog.Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.lineEdit.setValidator(QIntValidator())

        # Настройка списка со сплавами
        self.fusions_list = CatalogDataService.fusions_list()
        self.ui.comboBox.addItems(list(self.fusions_list.keys()))

        self.residuals_model = ResidualsModel(residuals)
        self.ui.leftoversTable.setModel(self.residuals_model)
        self.residuals_delegate = ResidualsSectionDelegate()
        self.ui.leftoversTable.setItemDelegate(self.residuals_delegate)
        self.residuals_delegate.deleteIndexClicked.connect(self.confirm_residual_removing)

        self.ui.leftover.clicked.connect(self.confirm_residual_adding)
        self.ui.finish.clicked.connect(self.confirm_order_completing)

    def confirm_residual_adding(self):
        
        if not self.ui.lineEdit.text():
            return
        
        data_row = {
            'num': self.residuals_model.counter,
            'length': self.ui.leftover_leigth.value(),
            'width': self.ui.leftover_width.value(),
            'height': self.ui.doubleSpinBox.value(),
            'batch': int(self.ui.lineEdit.text()),
            'fusion_id': self.fusions_list[self.ui.comboBox.currentText()],
        }
        self.residuals_model.appendRow(data_row)

    def confirm_residual_removing(self, index: QModelIndex):
        self.residuals_model.deleteRow(index.row())

    def confirm_order_completing(self):
        for row in range(self.residuals_model.rowCount()):
            r = self.residuals_model.index(row, 0, QModelIndex()).data(Qt.DisplayRole)
            fusions = CatalogDataService.fusions_list()
            fusion = fusions[r['fusion_id']]
            suc = StandardDataService.save_record(
                'ingots', length=r['length'], width=r['width'], height=r['height'],
                batch=r['batch'], fusion_id=fusion, status_id=2
            )
        self.accept()


class IngotAddingDialog(QDialog):

    ingotSavedSuccess = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = ui_add_ingot_dialog.Ui_Dialog()
        self.ui.setupUi(self)

        # Таймер для подсветки ошибки
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.cooldown)

        # Настройка списка со сплавами
        self.fusions = CatalogDataService.fusions_list()
        self.ui.fusion.addItems(list(self.fusions.keys()))

        self.ui.add.clicked.connect(self.confirm_adding)

    def confirm_adding(self):
        if not self.ui.batch.text():
            self.timer.start(1500)
            self.highlight()
            return
        
        batch = int(self.ui.batch.text())
        length = int(self.ui.length.value())
        width = int(self.ui.width.value())
        height = float(self.ui.height.value())
        fusion = self.fusions[self.ui.fusion.currentText()]

        id_ = StandardDataService.save_record('ingots', fusion_id=fusion, batch=batch, length=length, width=width, height=height)
        if not id_:
            QMessageBox.critical(self, 'Ошибка добавления', f'Слиток из партии {batch} не был добавлен в базу!',QMessageBox.Ok)
            return
        self.ingotSavedSuccess.emit({
            'id': id_,
            'order_id': None,
            'fusion_id': fusion,
            'status_id': 1,
            'size': [length, width, height],
            'batch': batch,
            'efficiency': 0.0,
        })

        QMessageBox.information(self, f'Партия {batch}', f'Слиток из партии {batch}\nуспешно добавлен!', QMessageBox.Ok)

    def highlight(self):
        QToolTip.showText(self.ui.batch.mapToGlobal(QPoint(0, 0)), 'Укажите номер партии', self.ui.batch)
        self.ui.batch.setStyleSheet('QLineEdit {border: 2px solid red; padding-left: -1px;}')

    def cooldown(self):
        self.ui.batch.setStyleSheet('')


class IngotAssignmentDialog(QDialog):

    predictedIngotSaved = pyqtSignal(dict, dict, BinNode)

    def __init__(self, order: dict, parent: typing.Optional[QWidget] = None) -> None:    
        super().__init__(parent)
        self.ui = ui_assign_ingot_dialog.Ui_Dialog()
        self.ui.setupUi(self)

        self.order = order
        self.predicted = False

        # Модель данных со свободными слитками
        self.ingot_model = IngotModel('unused')
        self.ingot_delegate = IngotSectionDelegate(False, self.ui.ingots_view)
        self.ui.ingots_view.setModel(self.ingot_model)
        self.ui.ingots_view.setItemDelegate(self.ingot_delegate)

        # Назначение меню кнопке
        self.fusions = CatalogDataService.fusions_list()
        fusions = list(self.parent().get_all_blanks().keys())
        if len(fusions) == 1:
            self.ui.predict.setText(f'Рассчитать {fusions[0]}')
            self.ui.predict.setObjectName(fusions[0])
            self.ui.predict.clicked.connect(self.calculate_ingot)
        else:
            self.menu = QMenu()
            self.directions = CatalogDataService.directions_list()
            for fusion in sorted(fusions, key=lambda item: self.fusions[item]):
                # Под каждый сплав создаётся отдельное событие выпадающего меню
                action: QAction = self.menu.addAction(fusion)
                action.setObjectName(fusion)
                action.triggered.connect(self.calculate_ingot)
            self.ui.predict.setMenu(self.menu)

        self.predicted_ingots: Dict[int, Dict] = dict()

        self.ui.add.clicked.connect(self.confirm_ingots_assinging)

    def confirm_ingots_assinging(self):
        if not self.ui.ingots_view.selectedIndexes():
            QMessageBox.critical(self, 'Ошибка добавления', 'Не выбраны слитки', QMessageBox.Close)
            return

        used_fusions = []
        # Проходим по всем выбранным слиткам
        for index in self.ui.ingots_view.selectedIndexes():
            ingot = self.ingot_model.data(index, Qt.DisplayRole)
            # Если текущий слиток <эфемерный>, то добавляем в базу
            if ingot['status_id'] == 4:
                predicted_tree = self.predicted_ingots[ingot['fusion_id']]['tree']
                predicted_efficiency = self.predicted_ingots[ingot['fusion_id']]['efficiency']
                ingot['id'] = StandardDataService.save_record(
                    'ingots', length=ingot['size'][0], width=ingot['size'][1], height=ingot['size'][2],
                    order_id=self.order['id'], status_id=3, efficiency=predicted_efficiency, fusion_id=ingot['fusion_id']
                )
                ingot['status_id'] = 3
                ingot['efficiency'] = predicted_efficiency
                self.predictedIngotSaved.emit({'id': self.order['id'], 'date': self.order['date']}, ingot, predicted_tree)
                used_fusions.append(ingot['fusion_id'])
                self.predicted = True
            # Если текущий слиток <слиток>, то обновляем связку
            else:
                StandardDataService.update_record('ingots', Field('id', ingot['id']), order_id=self.order['id'])
            ingot['order_id'] = self.order['id']
            self.parent().ingot_model.appendRow(ingot)
        self.update_statuses(used_fusions)
        self.accept()

    def repeatable_fusions(self):
        fusions = []
        for ingot in StandardDataService.get_by_field('ingots', Field('order_id', self.order['id'])):
            fusions.append(ingot[2])
        for index in self.ui.ingots_view.selectedIndexes():
            ingot = index.data(Qt.DisplayRole)
            if ingot['fusion_id'] in fusions:
                return True
            fusions.append(ingot['fusion_id'])
        return False

    def update_statuses(self, fusions: list):
        if not self.predicted_ingots:
            return

        model = self.parent().complect_model
        complect_counter = {}

        for row in range(model.rowCount(QModelIndex())):
            article = model.index(row, 0, QModelIndex())
            article_name = model.data(article, Qt.DisplayRole)

            # Переходим по всем заготовкам в изделии
            for sub_row in range(model.rowCount(article)):
                detail_fusion = int(model.data(model.index(sub_row, 3, article), Qt.DisplayRole))

                # Если не совпадают сплав заготовки и выбранного слитка - пропускаем
                if detail_fusion not in fusions:
                    continue

                # Собираем все нужные данные по колонкам
                name: str = model.data(model.index(sub_row, 0, article), Qt.DisplayRole)
                detail_id: int = model.data(model.index(sub_row, 1, article), Qt.DisplayRole)
                status_id_index = model.index(sub_row, 2, article)
                total_index = model.index(sub_row, 8, article)
                depth: float = model.data(model.index(sub_row, 6, article), Qt.DisplayRole)
                amount: int = model.data(model.index(sub_row, 7, article), Qt.DisplayRole)
                complect_counter[article_name + '_' + name] = {
                    'detail_id': int(detail_id),
                    'depth': float(depth),
                    'amount': int(amount),
                    'status_id': status_id_index,
                    'total': total_index,
                    'fusion_id': detail_fusion,
                }

        for fusion in self.predicted_ingots: 
            unplaced_counter = self.unplaced_list(fusion)

            # Сначала проходимся по счётчику неразмещённых заготовок
            updates = FieldCollection(['status_id', 'total', 'order_id', 'detail_id'])
            order = Field('order_id', self.order['id'])

            for name in unplaced_counter:
                detail = Field('detail_id', complect_counter[name]['detail_id'])
                if complect_counter[name]['fusion_id'] != fusion:
                    continue
                # Если количество заготовок совпадает с остатком
                if complect_counter[name]['amount'] == unplaced_counter[name]:
                    updates.append(Field('status_id', 4), Field('total', 0), order, detail)
                    model.setData(complect_counter[name]['status_id'], 4, Qt.EditRole)
                    model.setData(complect_counter[name]['total'], 0, Qt.EditRole)
                # Если количество заготовок не совпадает с остатком
                else:
                    updates.append(
                        Field('status_id', 5),
                        Field('total',complect_counter[name]['amount'] - unplaced_counter[name]),
                        order, detail
                    )
                    model.setData(complect_counter[name]['status_id'], 5, Qt.EditRole)
                    model.setData(complect_counter[name]['total'], complect_counter[name]['amount'] - unplaced_counter[name], Qt.EditRole)

            # В конце проходимся по всем заготовкам чтобы найти пропущенные толщины
            for name in complect_counter:
                detail = Field('detail_id', complect_counter[name]['detail_id'])
                if complect_counter[name]['fusion_id'] != fusion:
                    continue

                # Если количество неразмещённых заготовок равно нулю
                if name not in unplaced_counter:
                    updates.append(Field('status_id', 1), Field('total', complect_counter[name]['amount']), order, detail)
                    model.setData(complect_counter[name]['status_id'], 1, Qt.EditRole)
                    model.setData(complect_counter[name]['total'], complect_counter[name]['amount'], Qt.EditRole)
            OrderDataService.update_statuses(updates)

    def steps(self, fusion: int):
        """Список толщин"""
        leaves = self.predicted_ingots[fusion]['tree'].cc_leaves
        depth_list = [leave.bin.height for leave in leaves]
        return depth_list

    def unplaced_list(self, fusion: int):
        """Словарь неразмещенных заготовок {имя: количество}"""
        all_blanks = Counter(
            b.name for b in self.predicted_ingots[fusion]['tree'].root.kit
        )
        for leave in self.predicted_ingots[fusion]['tree'].cc_leaves:
            all_blanks -= Counter(b.name for b in leave.placed)
        return all_blanks

    def calculate_ingot(self):
        sender = self.sender()

        # По свойству objectName узнаём о выбранном сплаве
        fusion_name = sender.objectName()
        fusion_id = self.fusions[fusion_name]
        material = Material(fusion_name, 2.2, 1.)

        progress = QProgressDialog('OCI', 'Отмена', 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle('Рассчет слитка под ПЗ')
        progress.forceShow()
        # FIXME: получить имя заказа
        # FIXME: а имени может и не быть, расчёт слитков происходит при добавлении заказа
        order_name = 'НОВЫЙ ЗАКАЗ'
        progress.setLabelText('Процесс расчета слитка под ПЗ...')

        # details = self.parent().get_details_kit(material)
        details = self.parent().get_all_blanks()
        if material.name not in details:
            QMessageBox.information(
                self, 'Добавление слитка', 'Слитки такого сплава не найдены.',
                QMessageBox.Ok
            )
            progress.close()
            return
        details = self.parent().create_details_kit(
            details[material.name], material
        )

        log_operation_info(
            'start_ic',
            {
                'name': order_name, 'alloy': fusion_name,
                'blanks': details.qty(), 'heights': len(details.keys())
            },
        )

        try:
            sizes, tree, efficiency = self.predict_size(
                material, details, progress=progress
            )
            log_operation_info(
                'end_ic',
                {
                    'name': order_name, 'alloy': fusion_name,
                    'size': f'{sizes[0]}x{sizes[1]}x{sizes[2]}',
                    'efficiency': efficiency
                },
            )
        except ForcedTermination:
            log_operation_info(
                'user_inter_ic', {'name': order_name, 'alloy': fusion_name}
            )
            QMessageBox.information(self, 'Внимание', 'Процесс расчета слитка был прерван!', QMessageBox.Ok)
            return
        except Exception as exception:
            log_operation_info(
                'error_ic', {
                    'name': order_name, 'alloy': fusion_name, 'exception': exception
                }
            )
            QMessageBox.critical(
                self, 'Расчёт слитка завершился с ошибкой', f'{exception}', QMessageBox.Ok
            )
            return
        else:
            for row in range(self.ingot_model.rowCount()):
                ingot_index = self.ingot_model.index(row, 0, QModelIndex())
                if ingot_index.data(Qt.DisplayRole)['status_id'] == 1:
                    continue
                if fusion_id == ingot_index.data(Qt.DisplayRole)['fusion_id']:
                    self.ingot_model.deleteRow(row, QModelIndex())
                    break
            self.ingot_model.appendRow({
                'id': 0,
                'order_id': None,
                'status_id': 4,
                'fusion_id': fusion_id,
                'batch': None,
                'size': sizes,
            })
            self.ui.ingots_view.selectionModel().select(self.ingot_model.index(0, 0, QModelIndex()), QItemSelectionModel.SelectionFlag.Select)
            self.predicted_ingots[fusion_id] = {'tree': tree.root, 'efficiency': round(efficiency, 2)}
        progress.close()

    def predict_size(self, material: Material, kit: Kit, progress=None):
        max_size = self.ingot_settings['max_size']

        bin_ = Bin(*max_size, material=material)
        root = BinNode(bin_, kit=kit)
        tree = Tree(root)

        min_size = self.ingot_settings['min_size']

        # Дерево с рассчитанным слитком
        tree = self.parent().optimal_ingot_size(
            tree, min_size, max_size, self.settings, progress=progress
        )
        efficiency = round(solution_efficiency(tree.root, list(dfs(tree.root)), tree.main_kit, is_total=True), 2)
        print(f'Эффективность после расчета: {efficiency}')

        # size_error = self.ingot_settings['size_error']
        # allowance = self.ingot_settings['allowance']

        # Получение слитка с учетом погрешности и припусков
        length = tree.root.bin.length # + size_error + 2 * allowance
        width = tree.root.bin.width # + size_error + 2 * allowance
        height = tree.root.bin.height # + size_error + 2 * allowance

        return [math.ceil(length), math.ceil(width), math.ceil(height)], tree, efficiency

    def set_settings(self, settings: Dict, ingot_settings: Dict):
        self.settings = settings
        self.ingot_settings = ingot_settings


class IngotReadinessDialog(QDialog):
    def __init__(self, id: int, sizes: list, fusion: str, parent: typing.Optional[QWidget]) -> None:
        super().__init__(parent)
        self.ui = ui_ready_ingot_dialog.Ui_Dialog()
        self.ui.setupUi(self)

        self.id = id
        self.ui.length.setText(str(sizes[0]))
        self.ui.width.setText(str(sizes[1]))
        self.ui.heigth.setText(str(sizes[2]))
        self.ui.fusion.setText(fusion)
        self.ui.batch.setValidator(QIntValidator(1, 99999))

        # Таймер для подсветки ошибки
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.cooldown)

        self.ui.add.clicked.connect(self.confirm_readiness)

    def get_batch(self):
        return self.ui.batch.text()

    def confirm_readiness(self):
        batch = self.ui.batch.text()
        if not batch:
            self.timer.start(1500)
            self.highlight()
            return

        success = StandardDataService.update_record('ingots', Field('id', self.id), status_id=1, batch=batch)
        if not success:
            QMessageBox.critical(self, 'Ошибка добавления', f'Слиток из партии {batch} не был добавлен в базу.', QMessageBox.Ok)
            return

        self.accept()

    def highlight(self):
        QToolTip.showText(self.ui.batch.mapToGlobal(QPoint(0, 0)), 'Укажите номер партии', self.ui.batch)
        self.ui.batch.setStyleSheet('QLineEdit {border: 2px solid red; padding-left: -1px;}')

    def cooldown(self):
        self.ui.batch.setStyleSheet('')


class FullScreenWindow(QDialog):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = ui_full_screen.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.Window)

    def set_scene(self, scene: QGraphicsScene):
        self.ui.map.setScene(scene)
