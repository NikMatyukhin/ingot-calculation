import math
from enum import Enum
import pathlib
import pickle
from sequential_mh.bpp_dsc.support import dfs, eq_with_deformation_double_side, eq_with_deformation_one_side
from sequential_mh.bpp_dsc.tree import Tree, solution_efficiency
from typing import Any, Dict, List, Optional

from PyQt5.QtCore import (
    Qt, QAbstractItemModel, QModelIndex, QSortFilterProxyModel, pyqtSlot,
    QObject, QAbstractListModel
)
from PyQt5.QtWidgets import QApplication, QTreeView
from PyQt5.QtGui import QColor, QIcon, QPixmap

import application_rc

from service import (
    Field, StandardDataService, OrderDataService, FieldCollection
)

from widgets import OrderDelegate


class TreeItem:
    def __init__(self, data: list, parent: Optional[QObject] = None):
        self._item_data = data
        self._parent_item = parent
        self._child_items: List[TreeItem] = []

    def __repr__(self):
        return f'TreeItem({self._item_data})'

    def child(self, number: int):
        """Получение наследника по индексу

        :param number: Номер наследника
        :type number: int
        :return: Объект наследника
        :rtype: TreeItem
        """
        if number < 0 or number >= len(self._child_items):
            return None
        return self._child_items[number]

    def childCount(self) -> int:
        """Количество наследников у текущего объекта"""
        return len(self._child_items)

    def columnCount(self) -> int:
        """Количество полей данных у объекта дерева"""
        return len(self._item_data)

    def data(self, column: int) -> Any:
        """Получение данных по номеру колонки.

        :param column: Номер колонки
        :type column: int
        :return: Данные объекта
        :rtype: Any
        """
        if column < 0 or column >= len(self._item_data):
            return None
        return self._item_data[column]

    def insertChildren(self, position: int, count: int, columns: int) -> bool:
        """Вставка пустого места для добавляемых наследников.

        :param position: Позиция вставки
        :type position: int
        :param count: Количество наследников
        :type count: int
        :param columns: Количество колонок данных наследников
        :type columns: int
        :return: Результат операции вставки
        :rtype: bool
        """
        if position < 0 or position > len(self._child_items):
            return False

        for row in range(count):
            data = ['' for _ in range(columns)]
            self._child_items.insert(position, TreeItem(data, parent=self))
        return True

    def insertColumns(self, position: int, columns: int) -> bool:
        """Вставка пустого места под добавляемые колонки данных.

        :param position: Позиция вставки
        :type position: int
        :param columns: Количество колонок
        :type columns: int
        :return: Результат операции вставки
        :rtype: bool
        """
        if position < 0 or position > len(self._item_data):
            return False

        for column in range(columns):
            self._item_data.insert(position, None)

        for child_item in self._child_items:
            child_item.insertColumns(position, columns)
        return True

    def parent(self):
        """Получение предка объекта (предыдущий узел дерева)"""
        return self._parent_item

    def removeChildren(self, position: int, count: int) -> bool:
        """Удаление наследников у объекта.

        :param position: Позиция удаления
        :type position: int
        :param count: Количество удаляемых наследников
        :type count: int
        :return: Результат операции удаления
        :rtype: bool
        """
        if position < 0 or position + count > len(self._child_items):
            return False

        for row in range(count):
            del self._child_items[position]
        return True

    def removeColumns(self, position: int, columns: int) -> bool:
        """Удаление колонок данных у объекта.

        :param position: Позиция удаления
        :type position: int
        :param count: Количество удаляемых колонок
        :type count: int
        :return: Результат операции удаления
        :rtype: bool
        """
        if position < 0 or position + columns > len(self._item_data):
            return False

        for column in range(columns):
            del self._item_data[position]

        for child_item in self._child_items:
            child_item.removeColumns(position, columns)
        return True

    def childNumber(self) -> int:
        """Позиция текущего объекта среди наследников его родителя"""
        if self._parent_item:
            return self._parent_item._child_items.index(self)
        return 0

    def setData(self, column: int, value: Any) -> bool:
        """Замена конкретных данных объекта.

        :param column: Колонка замены
        :type column: int
        :param value: Заменяемое значение
        :type value: Any
        :return: Результат операции замены
        :rtype: bool
        """
        if column < 0 or column >= len(self._item_data):
            return False
        self._item_data[column] = value
        return True


class TreeModel(QAbstractItemModel):
    def __init__(self, headers: list, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.root_data = headers
        self.root_item = TreeItem(self.root_data)

    def get_item(self, index: QModelIndex) -> TreeItem:
        """Получение объекта-узла дерева по его индексу.

        Должен быть приватным методом, так как за пределами модели не нужен,
        но сделать его приватным не удаётся из-за наследников.

        :param index: Индекс получаемого объекта
        :type index: QModelIndex
        :return: Объект-узел дерева
        :rtype: TreeItem
        """
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item
        return self.root_item

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Количество наследников родителя parent.

        :param parent: Индекс родительского узла
        :type parent: QModelIndex
        :return: Количество наследников
        :rtype: int
        """
        parent_item = self.get_item(parent)
        return parent_item.childCount() if parent_item else 0

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Количество колонок данных родителя parent.

        :param parent: Индекс родительского узла
        :type parent: QModelIndex
        :return: Количество колонок
        :rtype: int
        """
        return self.root_item.columnCount()

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Установка флагов для взаимодействия с данными.

        :param index: Индекс объекта-узла
        :type index: QModelIndex
        :return: Набор флагов взаимодействия
        :rtype: Qt.ItemFlags
        """
        if not index.isValid():
            return Qt.NoItemFlags

        if index.column() == 0:
            return QAbstractItemModel.flags(self, index)

        return QAbstractItemModel.flags(self, index) | Qt.ItemIsEditable

    def index(self, row: int, column: int, parent: QModelIndex) -> QModelIndex:
        """Генерация модельных индексов.

        Необходимо наличие строки, колонки и родительского индекса для точного
        определения местоположения объекта-узла в древесной модели.

        :param row: Строка объекта
        :type row: int
        :param column: Колонка объекта
        :type column: int
        :param parent: Индекс родительского узла
        :type parent: QModelIndex
        :return: Сгенерированный индекс
        :rtype: QModelIndex
        """
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        parent_item = self.get_item(parent)
        if not parent_item:
            return QModelIndex()

        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)

        return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        """Получение родительского узла для узла с индексом index.

        :param index: Индекс дочернего узла
        :type index: QModelIndex
        :return: Индекс родительского узла
        :rtype: QModelIndex
        """
        if not index.isValid():
            return QModelIndex()

        child_item = self.get_item(index)
        parent_item = child_item.parent() if child_item else None

        if (parent_item == self.root_item or not parent_item):
            return QModelIndex()

        return self.createIndex(parent_item.childNumber(), 0, parent_item)

    def data(self, index: QModelIndex, role: int) -> Any:
        """Получение данных для объекта с адресом index по роли role.

        :param index: Индекс объекта-узла
        :type index: QModelIndex
        :param role: Тип необходимых данных (item-role)
        :type role: int
        :return: Данные объекта
        :rtype: Any
        """
        if not index.isValid():
            return None
        if role != Qt.DisplayRole:
            return None
        item = index.internalPointer()
        return item.data(index.column())

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int) -> Any:
        """Данные о заголовке модели.

        :param section: Номер секции
        :type section: int
        :param orientation: Направление заголовка
        :type orientation: Qt.Orientation
        :param role: Тип необходимых данных (item-role)
        :type role: int
        :return: Данные заголовка модели
        :rtype: Any
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.root_item.data(section)
        return None

    def setData(self, index: QModelIndex, value: object, role: int) -> bool:
        """Замена данных объекта с индексом index на данные value по роли role.

        :param index: Индекс объекта-узла
        :type index: QModelIndex
        :param value: Новое значение
        :type value: object
        :param role: Тип необходимых данных (item-role)
        :type role: int
        :return: Результат операции замены
        :rtype: bool
        """
        if index.isValid() and role == Qt.EditRole:
            item = self.get_item(index)
            result = item.setData(index.column(), value)
            if result:
                self.dataChanged.emit(index, index, [role])
            return result
        return False

    def setHeaderData(self, section: int, orientation: Qt.Orientation,
                      value: Any, role: int) -> bool:
        """замена данных о заголовках модели.

        :param section: Номер секции
        :type section: int
        :param orientation: Направление заголовка
        :type orientation: Qt.Orientation
        :param value: Новое значение
        :type value: Any
        :param role: Тип необходимых данных (item-role)
        :type role: int
        :return: Результат операции замены
        :rtype: bool
        """
        if orientation == Qt.Horizontal and role == Qt.EditRole:
            result = self.root_item.setData(section, value)
            if result:
                self.headerDataChanged(Qt.Horizontal, section, section)
            return result
        return False

    def appendRow(self, data: list, index: QModelIndex = QModelIndex()) -> bool:
        """Добавление к модели строки данных data для родителя index.

        :param data: Данные объекта-узла
        :type data: list
        :param index: Индекс родительского узла
        :type index: QModelIndex
        :return: Результат операции добавления
        :rtype: bool
        """
        if not self.insertRow(self.rowCount(index), index):
            return False

        parent_item = self.get_item(index)
        child_item = parent_item.child(parent_item.childCount() - 1)

        for i, field in enumerate(data):
            if isinstance(field, bool) or isinstance(field, Tree) or field is None or isinstance(field, dict):
                child_item.setData(i, field)
            else:
                child_item.setData(i, str(field))
        return True

    def insertColumns(self, position: int, columns: int,
                      parent: QModelIndex = QModelIndex()) -> bool:
        self.beginInsertColumns(parent, position, position + columns - 1)
        result = self.root_item.insertColumns(position, columns)
        self.endInsertColumns()
        return result

    def removeColumns(self, position: int, columns: int,
                      parent: QModelIndex = QModelIndex()) -> bool:
        self.beginRemoveColumns(parent, position, position + columns - 1)
        result = self.root_item.removeColumns(position, columns)
        self.endRemoveColumns()
        if self.root_item.columnCount() == 0:
            self.removeRows(0, self.root_item.childCount(), parent)
        return result

    def insertRow(self, row: int, parent: QModelIndex) -> bool:
        item = self.get_item(parent)
        if not item:
            return False

        self.beginInsertRows(parent, row, row + 1)
        result = item.insertChildren(row, 1, len(self.root_data))
        self.endInsertRows()
        return result

    def insertRows(self, position: int, rows: int,
                   parent: QModelIndex) -> bool:
        item = self.get_item(parent)
        if not item:
            return False

        self.beginInsertRows(parent, position, position + rows - 1)
        result = item.insertChildren(position, rows, len(self.root_data))
        self.endInsertRows()
        return result

    def removeRows(self, position: int, rows: int,
                   parent: QModelIndex) -> bool:
        item = self.get_item(parent)
        if not item:
            return False

        self.beginRemoveRows(parent, position, position + rows - 1)
        result = item.removeChildren(position, rows)
        self.endRemoveRows()
        return result

    def clear(self):
        self.beginResetModel()
        self.root_item.removeChildren(0, self.root_item.childCount())
        self.endResetModel()

    def setupModelData(self):
        pass


class TableModel(QAbstractItemModel):
    def __init__(self, headers: list, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.__headers = headers
        self.__items_data: List[List[Any]] = []

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags

        return QAbstractItemModel.flags(self, index)

    def parent(self, index: QModelIndex) -> QModelIndex:
        return QModelIndex()

    def data(self, index: QModelIndex, role: int) -> Any:
        if index.isValid() and role == Qt.DisplayRole or role == Qt.EditRole:
            return self.__items_data[index.row()][index.column()]
        return None

    def setData(self, index: QModelIndex, value: Any, role: int) -> bool:
        if index.isValid() and role == Qt.EditRole:
            self.__items_data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [role])
            return True
        return False

    def headerData(self, section: int, orientation: Qt.Orientation, role: int) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.__headers[section]
        return None

    def setHeaderData(self, section: int, orientation: Qt.Orientation, value: Any, role: int) -> bool:
        if orientation == Qt.Horizontal and role == Qt.EditRole:
            self.__headers[section] = value
            self.headerDataChanged(Qt.Horizontal, section, section)
            return True
        return False

    def index(self, row: int, column: int, parent: QModelIndex) -> QModelIndex:
        if parent.isValid():
            return QModelIndex()
        if 0 <= row < len(self.__items_data) and 0 <= column < len(self.__headers):
            item = self.__items_data[row][column]
            return self.createIndex(row, column, item)
        return QModelIndex()

    def rowCount(self, parent: QModelIndex) -> int:
        return len(self.__items_data)

    def columnCount(self, parent: QModelIndex) -> int:
        return len(self.__headers)

    def appendRow(self, data: list, index: QModelIndex) -> bool:
        if not self.insertRow(self.rowCount(QModelIndex()), index):
            return False
        self.__items_data[-1] = data
        return True

    def insertRow(self, row: int, parent: QModelIndex) -> bool:
        self.beginInsertRows(parent, row, row)
        self.__items_data.append([])
        self.endInsertRows()
        return True

    def removeRow(self, row: int, parent: QModelIndex) -> bool:
        self.beginRemoveRows(parent, row, row)
        self.__items_data.pop(row)
        self.endRemoveRows()
        return True

    def clear(self):
        self.beginResetModel()
        self.__items_data.clear()
        self.endResetModel()

    def setupModelData(self):
        pass


class ListModel(QAbstractListModel):
    def __init__(self, parent: Optional[QObject]) -> None:
        super().__init__(parent)
        self.items_data: List[Dict] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.items_data)

    def data(self, index: QModelIndex, role: int) -> Any:
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self.items_data[index.row()]
        return None

    def setData(self, index: QModelIndex, value: dict, role: int) -> bool:
        if index.isValid() and role == Qt.EditRole:
            self.items_data[index.row()].update(value)
            self.dataChanged.emit(index, index, [role])
            return True
        return False

    def appendRow(self, data: dict, index: QModelIndex = QModelIndex()) -> bool:
        if not self.insertRows(0, 1, index):
            return False
        self.items_data[0] = data
        return True

    def deleteRow(self, row: int, index: QModelIndex = QModelIndex()) -> bool:
        if 0 > row > len(self.items_data):
            return False
        return self.removeRows(row, 1, index)

    def clear(self):
        self.beginResetModel()
        self.items_data.clear()
        self.endResetModel()

    def insertRows(self, position: int, rows: int, parent: QModelIndex) -> bool:
        self.beginInsertRows(parent, position, position + rows - 1)
        self.items_data.insert(position, {})
        self.endInsertRows()
        return True

    def removeRows(self, position: int, rows: int, parent: QModelIndex) -> bool:
        self.beginRemoveRows(parent, position, position + rows - 1)
        for _ in range(rows):
            try:
                self.items_data.pop(position)
            except IndexError:
                return False
        self.endRemoveRows()
        return True


class OrderModel(TreeModel):
    def __init__(self, headers: list, parent: Optional[QObject] = None):
        super().__init__(headers, parent)
        self.__down_arrow = QPixmap(':icons/down-arrow.png')
        self.__progress_index = None
        self.__pending_index = None
        self.__closed_index = None
        self.setupModelData()

    def last(self, parent: QModelIndex):
        return self.index(self.rowCount(parent) - 1, 0, parent)

    def data(self, index: QModelIndex, role: int) -> Any:
        if not index.isValid():
            return None
        
        if role != Qt.DisplayRole and role != Qt.DecorationRole:
            return None

        if role == Qt.DecorationRole:
            if not index.parent().isValid():
                return self.__down_arrow

        item: TreeItem = index.internalPointer()
        # print(index.row(), index.column(), item.data(index.column()))
        return item.data(index.column())

    @property
    def progress_index(self) -> QModelIndex():
        return self.__progress_index

    @property
    def pending_index(self) -> QModelIndex():
        return self.__pending_index

    @property
    def closed_index(self) -> QModelIndex():
        return self.__closed_index

    def setupModelData(self):
        statuses = [
            tuple([Field('status_id', 1), Field('status_id', 2), 'В работе']),
            tuple([Field('status_id', 0), Field('status_id', 0), 'В ожидании']),
            tuple([Field('status_id', 3), Field('status_id', 3), 'Выполнено']),
        ]
        # TODO: строка для подгрузки заказов по статусу (нужно в будущем)
        # for order in OrderDataService.get_table(self.__status):
        for pair_status in statuses:
            table = OrderDataService.get_table(pair_status[:2])
            self.appendRow([pair_status[-1]], QModelIndex())
            for order in table:
                data_row = {
                    'id': order[0],
                    'status_id': order[1],
                    'name': order[2],
                    'date': order[3],
                    'step': order[4],
                    'efficiency': order[5],
                    'articles': order[6],
                    'details': order[7],
                    'thickness': order[8],
                }
                self.appendRow([data_row], self.index(self.rowCount() - 1, 0, QModelIndex()))
        self.__progress_index = self.index(0, 0, QModelIndex())
        self.__pending_index = self.index(1, 0, QModelIndex())
        self.__closed_index = self.index(2, 0, QModelIndex())


class IngotModel(ListModel):
    def __init__(self, category: OrderDataService.Category, 
                 fusions_id: List = None,
                 parent: Optional[QObject] = None) -> None:
        super(IngotModel, self).__init__(parent)
        self.__category = category
        self.__order_id = None
        self._fusions_id = fusions_id
        self.setupModelData()

    @property
    def order(self):
        return self.__order_id

    @order.setter
    def order(self, value):
        self.__order_id = value
        self.setupModelData()

    @order.deleter
    def order(self):
        self.__order_id = None

    def setupModelData(self):
        if self.items_data:
            self.clear()
        if self.__order_id:
            result = OrderDataService.ingots(Field('order_id', self.__order_id))
        else:
            result = OrderDataService.ware_ingots(self.__category)
        for ingot in reversed(result):
            if self._fusions_id is None or ingot[2] in self._fusions_id:
                data_row = {
                    'id': ingot[0],
                    'order_id': self.__order_id if self.__order_id else None,
                    'fusion_id': ingot[2],
                    'status_id': ingot[3],
                    'size': [ingot[4], ingot[5], round(ingot[6], 1)],
                    'batch': ingot[7],
                    'efficiency': ingot[8],
                    'number': ingot[9]
                }
                self.appendRow(data_row)


class SortIngotModel(QSortFilterProxyModel):
    """Сортировка слитков по объему и фильтрация по вместимости"""
    def __init__(self, parent: Optional[QObject], blanks=None) -> None:
        super().__init__(parent=parent)
        self.blanks = blanks
        self.invalidateFilter()

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        """Сравнение слитков по объему"""
        left_ingot = left.data(Qt.DisplayRole)
        right_ingot = right.data(Qt.DisplayRole)
        if not left_ingot or not right_ingot:
            return True
        left_volume = math.prod(left_ingot['size'])
        right_volume = math.prod(right_ingot['size'])
        return left_volume < right_volume

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """Фильтрация слитков по минимальным размерам"""
        index = self.sourceModel().index(source_row, 0, source_parent)
        ingot_data = index.data(Qt.DisplayRole)
        if not ingot_data:
            return True
        fusion: str = StandardDataService.get_by_id(
            'fusions', Field('id', ingot_data['fusion_id'])
        )[1]
        if self.blanks and fusion in self.blanks:
            for blank in self.blanks[fusion]:
                if ingot_data['size'][-1] >= blank.height:
                    size = blank.length, blank.width, blank.height
                    eq_with_one_side_def = eq_with_deformation_one_side(size, ingot_data['size'])
                    eq_with_two_side_def = eq_with_deformation_double_side(size, ingot_data['size'])
                    if eq_with_one_side_def or eq_with_two_side_def:
                        return True
            else:
                return False
        return True


class ResidualsModel(ListModel):
    def __init__(self, residuals: list, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.residuals = residuals
        self.counter = 1
        self.setupModelData()

    def appendRow(self, data: dict, index: QModelIndex = QModelIndex()) -> bool:
        if not self.insertRows(len(self.items_data), 1, index):
            return False
        self.items_data[-1] = data
        self.counter += 1
        return True

    def setupModelData(self):
        for r in self.residuals:
            data_row = {
                'num': self.counter,
                'length': int(r[0]),
                'width': int(r[1]),
                'height': round(r[2], 1),
                'fusion': r[3].name,
                'batch': r[4],
            }
            self.appendRow(data_row)


class IngotResidualsModel(TreeModel):
    def __init__(self, headers: list, parent: Optional[QObject] = None):
        super().__init__(headers, parent)
        self.__order_id: int = int()
    
    @property
    def order(self):
        return self.__order_id

    @order.setter
    def order(self, value):
        self.__order_id = value
        self.setupModelData()

    @order.deleter
    def order(self):
        self.__order_id = None

    def data(self, index: QModelIndex, role: int) -> Any:
        if not index.isValid():
            return None
        
        if role != Qt.DisplayRole:
            return None
        
        item: TreeItem = index.internalPointer()

        return item.data(index.column())

    def load_tree(self, path: pathlib.Path):
        """Загрузка корневого узла дерева из файла"""
        with path.open(mode='rb') as f:
            return pickle.load(f)

    def setupModelData(self):
        if not self.__order_id:
            return
        
        if self.rowCount(QModelIndex()):
            self.clear()
        
        ingots = OrderDataService.ingots(Field('order_id', self.__order_id))
        for ingot_n, ingot in enumerate(ingots):
            ingot_id, order_id, fusion_id, status_id, l, w, h, batch, efficiency, number = ingot
            
            # Цикл всегда на одну итерацию, либо на ноль если карты нет
            p = pathlib.Path() / 'schemes'
            for path in p.glob(f'{self.__order_id}_{ingot_id}*.oci'):
                fusion = StandardDataService.get_by_id('fusions', Field('id', fusion_id))[1]
                name = f'Слиток №{ingot_n + 1}'
                batch_ = f'(№{batch})' if batch else 'Не указана'
                size = f'{l}x{w}x{h}'
                tree: Tree = self.load_tree(path.absolute())
                t_efficiency: float = solution_efficiency(tree.root, list(dfs(tree.root)), tree.main_kit, is_total=True)
                self.appendRow([name, batch_, fusion, size, f'{round(t_efficiency * 100, 2)}%', tree], QModelIndex())

                counter = 1
                for node in tree.root.cc_leaves:
                    for subtree in node.subtree:
                        name = f'Остаток №{counter}'
                        l_, w_, h_ = subtree.root.bin.size
                        l_, w_, h_ = str(int(l_)), str(int(w_)), str(round(h_, 1))
                        size = 'x'.join([l_, w_, h_])
                        st_efficiency = solution_efficiency(subtree.root, list(dfs(subtree.root)), subtree.main_kit, is_total=True)
                        self.appendRow([name, batch_, fusion, size, f'{round(st_efficiency * 100, 2)}%', subtree], self.index(self.rowCount() - 1, 0, QModelIndex()))
                        counter += 1


class CatalogArticlesModel(TreeModel):
    def __init__(self, headers: list, parent: Optional[QObject] = None):
        super().__init__(headers, parent)
        self.__warning = QIcon(':icons/warning.png')
        self.setupModelData()

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags

        if index.column() == 0:
            return QAbstractItemModel.flags(self, index)

        return QAbstractItemModel.flags(self, index) | Qt.ItemIsEditable

    def data(self, index: QModelIndex, role: int) -> Any:
        if not index.isValid():
            return None

        if role != Qt.DisplayRole and role != Qt.EditRole and \
           role != Qt.DecorationRole and role != Qt.ToolTipRole:
            return None

        item: TreeItem = index.internalPointer()

        # HACK: для отображения иконки у изделия не должно быть заготовок,
        #       а сама иконка появляется всегда в первой колонке
        if item.childCount() == index.column() == 0:
            if role == Qt.DecorationRole:
                return self.__warning
            elif role == Qt.ToolTipRole:
                return 'Нет привязанных заготовок'

        return item.data(index.column())

    def setData(self, index: QModelIndex, value: object, role: int) -> bool:
        if not index.isValid():
            return False

        if role != Qt.EditRole:
            return False

        item = self.get_item(index)
        if item.setData(index.column(), value):
            self.dataChanged.emit(index, index, [role])

        return True

    def setupModelData(self):
        for line in sorted(StandardDataService.get_table('articles')):
            self.appendRow(line, QModelIndex())
            for sub_line in StandardDataService.get_by_field('details', Field('article_id', line[0])):
                self.appendRow([None, sub_line[4]], self.index(self.rowCount() - 1, 0, QModelIndex()))


class CatalogDetailsModel(TableModel):
    def __init__(self, headers: list, parent: Optional[QObject] = None):
        super().__init__(headers, parent)
        self.__article_id = None

    @property
    def article(self):
        return self.__article_id

    @article.setter
    def article(self, value):
        self.__article_id = value
        self.setupModelData()

    @article.deleter
    def article(self):
        self.__article_id = None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        if index.column == 8:
            return QAbstractItemModel.flags(self, index)
        return QAbstractItemModel.flags(self, index) | Qt.ItemIsEditable

    def data(self, index: QModelIndex, role: int) -> Any:
        if not index.isValid():
            return None

        if role != Qt.DisplayRole and role != Qt.EditRole:
            return None

        return super().data(index, role)

    def setupModelData(self):
        if self.rowCount(QModelIndex()):
            self.clear()

        for line in StandardDataService.get_by_field('details', Field('article_id', self.__article_id)):
            id, _, fusion_id, direction_id, name, l, w, h, a, p = line
            self.appendRow([name, fusion_id, l, w, h, a, p, direction_id, id], QModelIndex())


class ComplectsModel(TreeModel):
    def __init__(self, headers: list, parent: Optional[QObject] = None):
        super().__init__(headers, parent)
        self.setupModelData()

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        if index.column() == 6 or index.column() == 7:
            return QAbstractItemModel.flags(self, index) | Qt.ItemIsEditable
        return QAbstractItemModel.flags(self, index)

    def data(self, index: QModelIndex, role: int) -> Any:
        if not index.isValid():
            return None
        if role != Qt.DisplayRole and role != Qt.EditRole and role != Qt.TextAlignmentRole:
            return None

        item = index.internalPointer()

        if role == Qt.TextAlignmentRole:
            if index.column() not in [1, 2, 8]:
                return Qt.AlignHCenter
            else:
                return Qt.AlignLeft

        return item.data(index.column())

    def added(self):
        added_ = {
            'articles_count': 0,
            'details_count': 0,
            'complects': {}
        }
        for article in self.root_item._child_items:
            if not article.data(10):
                continue
            added_['complects'][article.data(0)] = []
            added_['articles_count'] += 1
            for detail in article._child_items:
                if detail.data(10):
                    d_ = detail.data(9), detail.data(6), detail.data(7)
                    added_['complects'][article.data(0)].append(d_)
                    added_['details_count'] += int(detail.data(6))
        return added_

    def setupModelData(self):
        for article in StandardDataService.get_table('articles'):
            article_id, name = article
            self.appendRow([article_id, name, None, None, None, None, None, None, None, None, False], QModelIndex())

            # Получение индекса только что добавленной записи изделия
            detail = StandardDataService.get_by_field('details', Field('article_id', article_id))

            # Для удаления из списка изеделий без заготовок
            if not detail:
                continue
            parent = self.index(self.rowCount() - 1, 0, QModelIndex())
            # Выполнение для всех деталей, связанных с заданной ведомостью
            for sub_line in detail:
                detail_id, _, fusion_id, direction_id, name, l, w, d, amount, priority = sub_line
                self.appendRow([article_id, name, fusion_id, l, w, d, amount, priority, direction_id, detail_id, False], parent)


class OrderInformationComplectsModel(TreeModel):

    class Col(Enum):
        NAME = 0
        ID = 1
        STATUS = 2
        FUSION = 3
        LENGTH = 4
        WIDTH = 5
        HEIGHT = 6
        AMOUNT = 7
        TOTAL = 8
        PRIORITY = 9
        DIRECTION = 10
    EDITABLE_COLUMNS = [Col.AMOUNT, Col.PRIORITY]
    SIZE_COLUMNS = [Col.LENGTH, Col.WIDTH, Col.HEIGHT]
    NUMERIC_COLUMNS = SIZE_COLUMNS + EDITABLE_COLUMNS + [Col.TOTAL]
    AVAILABLE_DATA_ROLES = (Qt.DisplayRole, Qt.EditRole, Qt.TextAlignmentRole,
                            Qt.BackgroundRole)

    def __init__(self, headers: list, parent: Optional[QObject] = None):
        super(OrderInformationComplectsModel, self).__init__(headers, parent=parent)
        self.__order_id: int = 0

    @property
    def order(self):
        return self.__order_id

    @order.setter
    def order(self, value):
        self.__order_id = value
        self.setupModelData()

    @order.deleter
    def order(self):
        self.__order_id = None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        # Проверка валидности индекса, чтобы не вернуть флаги для root
        if not index.isValid():
            return Qt.NoItemFlags

        # Разрешение редактирования колонок с количеством и приоритетом
        if index.column() in self.EDITABLE_COLUMNS:
            return QAbstractItemModel.flags(self, index) | Qt.ItemIsEditable

        return QAbstractItemModel.flags(self, index)

    def data(self, index: QModelIndex, role: int) -> Any:
        # Проверка валидности индекса, чтобы не вернуть root данные
        if not index.isValid():
            return None

        # Проверка переданных ролей
        if role not in self.AVAILABLE_DATA_ROLES:
            return None

        item = index.internalPointer()

        # Оцентровка всех колонок с цифровыми значениями
        if role == Qt.TextAlignmentRole:
            if self.Col(index.column()) in self.NUMERIC_COLUMNS:
                return Qt.AlignHCenter
            else:
                return Qt.AlignLeft

        # Окраска строк заготовок в соответствии со статусом
        if role == Qt.BackgroundRole:
            status = item.data(2)
            if isinstance(status, str) and status.isdigit():
                if int(status) == 2:
                    return QColor('#a2ff85')
                if int(status) == 3:
                    return QColor('#fa6464')
                if int(status) == 4:
                    return QColor('#ffff88')
                if int(status) == 5:
                    return QColor('#ffb34d')
                if int(status) == 6:
                    return QColor('#bbdaff')

        return item.data(index.column())

    def discard_statuses(self, order_id: int, fusion_id: int):
        updates = FieldCollection(
            ['status_id', 'order_id', 'detail_id']
        )
        order, status = Field('order_id', order_id), Field('status_id', 0)
        for article in self.root_item._child_items:
            for detail in article._child_items:
                if int(detail.data(3)) != fusion_id:
                    continue
                updates.append(status, order, Field('detail_id', detail.data(1)))
        OrderDataService.discard_statuses(updates)

    def setupModelData(self):
        if self.root_item.childCount():
            self.clear()
        if not self.__order_id:
            return

        complects = OrderDataService.complects(Field('order_id', self.__order_id))
        for article in complects:
            article_id, name = article
            self.appendRow([name, article_id, None, None, None, None, None, None, None, None, None], QModelIndex())

            # Получение индекса только что добавленной записи изделия
            parent = self.index(self.rowCount() - 1, 0, QModelIndex())
            detail = complects[article]            

            # Выполнение для всех деталей, связанных с заданной ведомостью
            for sub_line in detail:
                detail_id, fusion_id, direction_id, status_id, name, l, w, d, amount, total, priority = sub_line
                self.appendRow([name, detail_id, status_id, fusion_id, l, w, d, amount, total, priority, direction_id], parent)


class CatalogFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.name_filter = str('')

    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex) -> bool:
        index = self.sourceModel().index(sourceRow, 0, sourceParent)
        if not index.parent().isValid():
            name = self.sourceModel().data(
                self.sourceModel().index(sourceRow, 1, QModelIndex()),
                Qt.DisplayRole
            )
            if name:
                return self.name_filter in name.lower()
        return True

    @pyqtSlot(str)
    def name(self, filter: str):
        self.name_filter = filter.lower()
        self.invalidateFilter()


class OrderComplectsFilterProxyModel(QSortFilterProxyModel):
    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex) -> bool:
        index = self.sourceModel().index(sourceRow, 0, sourceParent)
        if not index.parent().isValid():
            return self.sourceModel().data(self.sourceModel().index(sourceRow, 10, QModelIndex()), Qt.DisplayRole)
        else:
            return self.sourceModel().data(self.sourceModel().index(sourceRow, 10, index.parent()), Qt.DisplayRole)
