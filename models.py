import application_rc

from typing import NoReturn, List, Any

from PySide6.QtCore import (Qt, QAbstractItemModel, QModelIndex,
                            QSortFilterProxyModel, Slot)
from PySide6.QtGui import (QIcon)

from service import (StandardDataService)


class TreeItem:

    def __init__(self, data: list, parent=None):
        self.__item_data = data
        self.__parent_item = parent
        self.__child_items = []

    def child(self, number: int):

        if number < 0 or number >= len(self.__child_items):
            return None
        return self.__child_items[number]

    def childCount(self) -> int:

        return len(self.__child_items)

    def columnCount(self) -> int:

        return len(self.__item_data)

    def data(self, column: int) -> Any:

        if column < 0 or column >= len(self.__item_data):
            return None
        return self.__item_data[column]

    def insertChildren(self, position: int, count: int, columns: int) -> bool:

        if position < 0 or position > len(self.__child_items):
            return False

        for row in range(count):
            data = ['' for _ in range(columns)]
            self.__child_items.insert(position, TreeItem(data, parent=self))
        return True

    def insertColumns(self, position: int, columns: int) -> bool:

        if position < 0 or position > len(self.__item_data):
            return False

        for column in range(columns):
            self.__item_data.insert(position, None)

        for child_item in self.__child_items:
            child_item.insertColumns(position, columns)

    def parent(self):

        return self.__parent_item

    def removeChildren(self, position: int, count: int) -> bool:

        if position < 0 or position + count > len(self.__child_items):
            return False

        for row in range(count):
            del self.__child_items[position]
        return True

    def removeColumns(self, position: int, columns: int) -> bool:

        if position < 0 or position + columns > len(self.__item_data):
            return False

        for column in range(columns):
            del self.__item_data[position]

        for child_item in self.__child_items:
            child_item.removeColumns(position, columns)

    def childNumber(self) -> int:

        if self.__parent_item:
            return self.__parent_item.__child_items.index(self)
        return 0

    def setData(self, column: int, value: Any) -> bool:

        if column < 0 or column >= len(self.__item_data):
            return False
        self.__item_data[column] = value
        return True


class TreeModel (QAbstractItemModel):

    def __init__(self, headers, parent=None):

        super(TreeModel, self).__init__(parent)
        self.root_data = headers
        self.root_item = TreeItem(self.root_data)
        self.__warning = QIcon(':icons/warning.png')
        self.setupModelData()

    def get_item(self, index: QModelIndex) -> TreeItem:

        if index.isValid():
            item = index.internalPointer()
            if item:
                return item
        return self.root_item

    def rowCount(self, parent: QModelIndex) -> int:

        parent_item = self.get_item(parent)
        return parent_item.childCount() if parent_item else 0

    def columnCount(self, parent: QModelIndex) -> int:

        return self.root_item.columnCount()

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:

        if not index.isValid():
            return Qt.NoItemFlags

        if index.column() == 0:
            return QAbstractItemModel.flags(self, index)

        return QAbstractItemModel.flags(self, index) | Qt.ItemIsEditable

    def index(self, row: int, column: int, parent: QModelIndex) -> QModelIndex:

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

        if not index.isValid():
            return QModelIndex()

        child_item = self.get_item(index)
        parent_item = child_item.parent() if child_item else None

        if (parent_item == self.root_item or not parent_item):
            return QModelIndex()

        return self.createIndex(parent_item.childNumber(), 0, parent_item)

    def data(self, index: QModelIndex, role: int) -> Any:

        if not index.isValid():
            return None

        if role != Qt.DisplayRole and role != Qt.EditRole and \
           role != Qt.DecorationRole and role != Qt.ToolTipRole:
            return None

        item = index.internalPointer()

        if item.childCount() == index.column() == 0:
            if item.parent() is self.root_item:
                if role == Qt.DecorationRole:
                    return self.__warning
                elif role == Qt.ToolTipRole:
                    return 'Не подвязан ни один артикул'

        return item.data(index.column())

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int) -> Any:

        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.root_item.data(section)
        return None

    def setData(self, index: QModelIndex, value: object, role: int) -> bool:

        if index.isValid() and role == Qt.EditRole:
            item = self.get_item(index)
            result = item.setData(index.column(), value)
            if result:
                self.dataChanged.emit(index, index, [role])
            return result
        return False

    def setHeaderData(self, section: int, orientation: Qt.Orientation,
                      value: Any, role: int) -> bool:

        if orientation == Qt.Horizontal and role == Qt.EditRole:
            result = self.root_item.setData(section, value)
            if result:
                self.headerDataChanged(Qt.Horizontal, section, section)
            return result
        return False

    def appendRow(self, data: List[Any], index: QModelIndex) -> bool:

        if not self.insertRows(0, 1, index):
            return False

        parent_item = self.get_item(index)
        child_item = parent_item.child(0)

        for i, field in enumerate(data):
            if type(field) is bool or field is None:
                child_item.setData(i, field)
            else:
                child_item.setData(i, str(field))

    def insertColumns(self, position: int, columns: int,
                      parent: QModelIndex) -> bool:

        self.beginInsertColumns(parent, position, position + columns - 1)
        result = self.root_item.insertColumns(position, columns)
        self.endInsertColumns()
        return result

    def removeColumns(self, position: int, columns: int,
                      parent: QModelIndex) -> bool:

        self.beginRemoveColumns(parent, position, position + columns - 1)
        result = self.root_item.removeColumns(position, columns)
        self.endRemoveColumns()
        if self.root_item.columnCount() == 0:
            self.removeRows(0, self.root_item.childCount())
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

    def setupModelData(self):
        pass


class CatalogModel (TreeModel):

    def setData(self, index: QModelIndex, value: object, role: int) -> bool:

        parent = self.parent(index)
        if not parent.isValid():
            if index.column() == 3 and role == Qt.EditRole:
                return False

        if index.isValid() and role == Qt.EditRole:
            item = self.get_item(index)
            result = item.setData(index.column(), value)
            if result:
                self.dataChanged.emit(index, index, [role])
            return result
        return False

    def setupModelData(self):

        for line in StandardDataService.get_table('products'):
            key, type, designation = line
            self.appendRow([key, type, designation, None, None], QModelIndex())

            sub = StandardDataService.get_by_field('articles', register_id=key)
            parent = self.index(0, 0, QModelIndex())

            for sub_line in sub:
                id, key, nomen, rent = sub_line
                rent = ['Нет', 'Да'][rent]
                self.appendRow([None, type, nomen, rent, id], parent)


class ComplectsModel (TreeModel):

    def data(self, index: QModelIndex, role: int) -> Any:

        if not index.isValid():
            return None

        if role != Qt.DisplayRole and role != Qt.EditRole:
            return None

        item = index.internalPointer()

        return item.data(index.column())

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:

        if not index.isValid():
            return Qt.NoItemFlags
        if index.column() == 6 or index.column() == 7:
            return QAbstractItemModel.flags(self, index) | Qt.ItemIsEditable
        return QAbstractItemModel.flags(self, index)

    def setupModelData(self):

        for line in StandardDataService.get_table('articles'):
            id, key, nomen, rent = line
            rent = ['Нет', 'Да'][rent]
            self.appendRow(
                [key, nomen, rent, None, None, None, None, None, id, False],
                QModelIndex()
            )

            sub = StandardDataService.get_by_field('details', register_id=key)
            if not sub:
                self.removeRows(0, 1, QModelIndex())

            parent = self.index(0, 0, QModelIndex())

            for sub_line in sub:
                id, _, _, name, l, w, d, amount, priority, _ = sub_line
                self.appendRow(
                    [key, name, None, l, w, d, amount, priority, id, False],
                    parent
                )


class ProductInformationFilterProxyModel (QSortFilterProxyModel):

    def __init__(self, parent=None):
        super(ProductInformationFilterProxyModel, self).__init__(parent)
        self.register_filter = ''
        self.designtaion_filter = ''
        self.nomenclature_filter = ''
        self.rent_filter = ''
        self.type_filter = ''

    def filterAcceptsRow(self, sourceRow: int,
                         sourceParent: QModelIndex) -> bool:

        index = self.sourceModel().index(sourceRow, 0, sourceParent)
        if index.parent().isValid():
            nomenclature = self.sourceModel().data(
                self.sourceModel().index(sourceRow, 2, sourceParent),
                Qt.DisplayRole
            )
            rent = self.sourceModel().data(
                self.sourceModel().index(sourceRow, 3, sourceParent),
                Qt.DisplayRole
            )
            return self.nomenclature_filter in nomenclature and \
                self.rent_filter in rent
        else:
            register = str(self.sourceModel().data(
                self.sourceModel().index(sourceRow, 0, QModelIndex()),
                Qt.DisplayRole)
            )
            product_type = self.sourceModel().data(
                self.sourceModel().index(sourceRow, 1, QModelIndex()),
                Qt.DisplayRole
            )
            designation = self.sourceModel().data(
                self.sourceModel().index(sourceRow, 2, QModelIndex()),
                Qt.DisplayRole
            )
            return self.type_filter in product_type and \
                self.register_filter in register and \
                self.designtaion_filter in designation

    @Slot(str)
    def setRegister(self, filter: str) -> NoReturn:
        self.register_filter = filter
        self.invalidateFilter()

    @Slot(str)
    def setDesignation(self, filter: str) -> NoReturn:
        self.designtaion_filter = filter
        self.invalidateFilter()

    @Slot(str)
    def setNomenclature(self, filter: str) -> NoReturn:
        self.nomenclature_filter = filter
        self.invalidateFilter()

    @Slot(bool)
    def setRent(self, filter: str) -> NoReturn:
        if filter:
            self.rent_filter = 'Да'
        else:
            self.rent_filter = ''
        self.invalidateFilter()

    @Slot(str)
    def setType(self, filter: str) -> NoReturn:
        if filter == 'Все изделия':
            filter = ''
        self.type_filter = filter
        self.invalidateFilter()


class ArticleInformationFilterProxyModel (QSortFilterProxyModel):

    def __init__(self, parent=None):
        super(ArticleInformationFilterProxyModel, self).__init__(parent)
        self.nomenclature_filter = ''

    def filterAcceptsRow(self, sourceRow: int,
                         sourceParent: QModelIndex) -> bool:

        index = self.sourceModel().index(sourceRow, 0, sourceParent)
        if not index.parent().isValid():
            nomenclature = self.sourceModel().data(
                self.sourceModel().index(sourceRow, 1, QModelIndex()),
                Qt.DisplayRole
            )
            return self.nomenclature_filter in nomenclature
        return True

    @Slot(str)
    def setNomenclature(self, filter: str) -> NoReturn:
        self.nomenclature_filter = filter
        self.invalidateFilter()


class NewOrderFilterProxyModel (QSortFilterProxyModel):

    def filterAcceptsRow(self, sourceRow: int,
                         sourceParent: QModelIndex) -> bool:

        index = self.sourceModel().index(sourceRow, 0, sourceParent)
        if not index.parent().isValid():
            return self.sourceModel().data(
                self.sourceModel().index(sourceRow, 9, QModelIndex()),
                Qt.DisplayRole
            )
        else:
            return self.sourceModel().data(
                self.sourceModel().index(sourceRow, 9, index.parent()),
                Qt.DisplayRole
            )
        return False
