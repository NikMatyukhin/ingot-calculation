import typing
import application_rc
from typing import List, Dict, Any

from PySide6.QtCore import (
    Qt, QAbstractItemModel, QModelIndex, QSortFilterProxyModel, Slot, QObject,
    QAbstractListModel
)
from PySide6.QtGui import (
    QBrush, QColor, QIcon
)

from service import (
    StandardDataService, OrderDataService
)


class TreeItem:

    def __init__(self, data: list, parent: typing.Optional[QObject] = None):
        self.__item_data = data
        self.__parent_item = parent
        self.__child_items = []

    def child(self, number: int):
        """Получение наследника по индексу

        :param number: Номер наследника
        :type number: int
        :return: Объект наследника
        :rtype: TreeItem
        """
        if number < 0 or number >= len(self.__child_items):
            return None
        return self.__child_items[number]

    def childCount(self) -> int:
        """Количество наследников у текущего объекта"""
        return len(self.__child_items)

    def columnCount(self) -> int:
        """Количество полей данных у объекта дерева"""
        return len(self.__item_data)

    def data(self, column: int) -> Any:
        """Получение данных по номеру колонки.

        :param column: Номер колонки
        :type column: int
        :return: Данные объекта
        :rtype: Any
        """
        if column < 0 or column >= len(self.__item_data):
            return None
        return self.__item_data[column]

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
        if position < 0 or position > len(self.__child_items):
            return False

        for row in range(count):
            data = ['' for _ in range(columns)]
            self.__child_items.insert(position, TreeItem(data, parent=self))
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
        if position < 0 or position > len(self.__item_data):
            return False

        for column in range(columns):
            self.__item_data.insert(position, None)

        for child_item in self.__child_items:
            child_item.insertColumns(position, columns)

    def parent(self):
        """Получение предка объекта (предыдущий узел дерева)"""
        return self.__parent_item

    def removeChildren(self, position: int, count: int) -> bool:
        """Удаление наследников у объекта.

        :param position: Позиция удаления
        :type position: int
        :param count: Количество удаляемых наследников
        :type count: int
        :return: Результат операции удаления
        :rtype: bool
        """
        if position < 0 or position + count > len(self.__child_items):
            return False

        for row in range(count):
            del self.__child_items[position]
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
        if position < 0 or position + columns > len(self.__item_data):
            return False

        for column in range(columns):
            del self.__item_data[position]

        for child_item in self.__child_items:
            child_item.removeColumns(position, columns)

    def childNumber(self) -> int:
        """Позиция текущего объекта среди наследников его родителя"""
        if self.__parent_item:
            return self.__parent_item.__child_items.index(self)
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
        if column < 0 or column >= len(self.__item_data):
            return False
        self.__item_data[column] = value
        return True


class TreeModel(QAbstractItemModel):

    def __init__(self, headers, parent=None):
        super(TreeModel, self).__init__(parent)
        self.root_data = headers
        self.root_item = TreeItem(self.root_data)
        self.__warning = QIcon(':icons/warning.png')

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

    def rowCount(self, parent: QModelIndex) -> int:
        """Количество наследников родителя parent.

        :param parent: Индекс родительского узла
        :type parent: QModelIndex
        :return: Количество наследников
        :rtype: int
        """
        parent_item = self.get_item(parent)
        return parent_item.childCount() if parent_item else 0

    def columnCount(self, parent: QModelIndex) -> int:
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

    def appendRow(self, data: List[Any], index: QModelIndex) -> bool:
        """Добавление к модели строки данных data для родителя index.

        :param data: Данные объекта-узла
        :type data: List[Any]
        :param index: Индекс родительского узла
        :type index: QModelIndex
        :return: Результат операции добавления
        :rtype: bool
        """
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


class ListModel(QAbstractListModel):
    
    def __init__(self, parent: typing.Optional[QObject]) -> None:
        super(ListModel, self).__init__(parent)
        self.items_data = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.items_data)
    
    def data(self, index: QModelIndex, role: int) -> typing.Any:
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self.items_data[index.row()]
        return None
    
    def setData(self, index: QModelIndex, value: Dict, role: int) -> bool:
        if index.isValid() and role == Qt.EditRole:
            self.items_data[index.row()].update(value)
            self.dataChanged.emit(index, index, [role])
            return True
        return False

    def appendRow(self, data: Dict, index: QModelIndex = QModelIndex()) -> bool:
        if not self.insertRows(0, 1, index):
            return False
        self.items_data[-1] = data
    
    def deleteRow(self, row: int, index: QModelIndex = QModelIndex()) -> bool:
        if 0 > row > len(self.items_data):
            return False
        return self.removeRows(row, 1, index)

    def insertRows(self, position: int, rows: int, parent: QModelIndex) -> bool:
        self.beginInsertRows(parent, position, position + rows - 1)
        self.items_data.append({})
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


class OrderModel(ListModel):

    def __init__(self, parent: typing.Optional[QObject] = None):
        super(OrderModel, self).__init__(parent)
        self.setupModelData()

    def extradata(self, index: QModelIndex, role: int, field: str = None) -> typing.Any:
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            if field:
                data_row = self.items_data[index.row()]
                try:
                    value = data_row[field]
                except KeyError:
                    if field == 'status_name':
                        value = StandardDataService.get_by_id('orders_statuses', {'status_id': data_row['status_id']})[1]
                    elif field == 'detail_number':
                        value = OrderDataService.details_count({'order_id': data_row['order_id']})
                    elif field == 'article_number':
                        value = OrderDataService.articles_count({'order_id': data_row['order_id']})
                    else:
                        value = 'Ошибка!'
                return value
            else:
                return self.items_data[index.row()]
        return None

    def setupModelData(self):
        for order in OrderDataService.get_table_2():
            data_row = {
                'order_id': order[0],
                'status_id': order[2],
                'order_name': order[3],
                'current_depth': order[4],
                'efficiency': order[5],
                'creation_date': order[7],
            }
            self.appendRow(data_row)


class IngotModel(ListModel):

    def __init__(self, parent: typing.Optional[QObject] = None) -> None:
        super(IngotModel, self).__init__(parent)
        self.__order_id = None
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
    
    def extradata(self, index: QModelIndex, role: int, field: str = None) -> typing.Any:
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            if field:
                data_row = self.items_data[index.row()]
                try:
                    value = data_row[field]
                except KeyError:
                    if field == 'fusion_name':
                        value = StandardDataService.get_by_id('fusions', {'fusion_id': data_row['fusion_id']})[1]
                    elif field == 'background':
                        value = StandardDataService.get_by_id('ingots_statuses', {'status_id': data_row['status_id']})[2]
                    else:
                        value = 'Ошибка!'
                return value
            else:
                return self.items_data[index.row()]
        return None

    def clear(self):
        self.beginResetModel()
        self.items_data.clear()
        self.endResetModel()

    def setupModelData(self):
        if self.items_data:
            self.clear()
        if self.__order_id:
            result = OrderDataService.ingots({'order_id': self.__order_id})
        else:
            result = OrderDataService.vacancy_ingots()
        for ingot in result:
            data_row = {
                'ingot_id': ingot[0],
                'fusion_id': ingot[1],
                'ingot_part': ingot[3],
                'ingot_size': [round(ingot[4]), round(ingot[5]), round(ingot[6], 1)],
                'status_id': ingot[7],
                'efficiency': ingot[8]
            }
            self.appendRow(data_row)


class CatalogModel(TreeModel):

    def __init__(self, headers: list, parent: typing.Optional[QObject] = None):
        super(CatalogModel, self).__init__(headers, parent)
        self.setupModelData()

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

            sub = StandardDataService.get_by_field('articles', product_id=key)
            parent = self.index(0, 0, QModelIndex())

            for sub_line in sub:
                id, key, nomen, rent = sub_line
                rent = ['Нет', 'Да'][rent]
                self.appendRow([None, type, nomen, rent, id], parent)


class ComplectsModel(TreeModel):

    def __init__(self, headers: list, parent: typing.Optional[QObject] = None):
        super(ComplectsModel, self).__init__(headers, parent)
        self.setupModelData()

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        if index.column() == 7 or index.column() == 8:
            return QAbstractItemModel.flags(self, index) | Qt.ItemIsEditable
        return QAbstractItemModel.flags(self, index)

    def data(self, index: QModelIndex, role: int) -> Any:
        if not index.isValid():
            return None
        if role != Qt.DisplayRole and role != Qt.EditRole:
            return None
        item = index.internalPointer()
        if index.parent().isValid():
            if index.column() == 3:
                fusion = StandardDataService.get_by_id('fusions',{'fusion_id': item.data(3)})[1]
                return fusion if fusion else 'Ошибка!'
        return item.data(index.column())

    def realdata(self, index: QModelIndex, role: int) -> Any:
        if not index.isValid():
            return None
        if role != Qt.DisplayRole and role != Qt.EditRole and role != Qt.BackgroundRole and role != Qt.ForegroundRole:
            return None
        item = index.internalPointer()
        return item.data(index.column())

    def setupModelData(self):
        for article in StandardDataService.get_table('articles'):
            article_id, product_id, nomen, rent = article
            rent = ['Нет', 'Да'][rent]
            self.appendRow([product_id, nomen, rent, None, None, None, None, None, None, None, article_id, False], QModelIndex())

            # Получение индекса только что добавленной записи изделия
            parent = self.index(0, 0, QModelIndex())
            detail = StandardDataService.get_by_field('details', product_id=product_id)
            
            # Для удаления из списка изеделий без заготовок
            if not detail:
                self.removeRows(0, 1, QModelIndex())
            
            # Выполнение для всех деталей, связанных с заданной ведомостью
            for sub_line in detail:
                detail_id, _, fusion_id, name, l, w, d, amount, priority, direction_id = sub_line
                self.appendRow([product_id, name, None, fusion_id, l, w, d, amount, priority, direction_id, detail_id, False], parent)


class OrderInformationComplectsModel(TreeModel):

    def __init__(self, headers: list, parent: typing.Optional[QObject] = None):
        super(OrderInformationComplectsModel, self).__init__(headers, parent=parent)
        self.__order_id = None

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
        if not index.isValid():
            return Qt.NoItemFlags
        if index.column() == 7 or index.column() == 8:
            return QAbstractItemModel.flags(self, index) | Qt.ItemIsEditable
        return QAbstractItemModel.flags(self, index)

    def data(self, index: QModelIndex, role: int) -> Any:
        if not index.isValid():
            return None
        if role != Qt.DisplayRole and role != Qt.EditRole and role != Qt.BackgroundRole and role != Qt.ForegroundRole:
            return None
        item = index.internalPointer()
        status_id = item.data(2)
        fusion_id = item.data(3)
        direction_id = item.data(9)
        if index.parent().isValid():
            if role == Qt.BackgroundRole:
                background = StandardDataService.get_by_id('complects_statuses', {'status_id': status_id})[2]
                return QBrush(QColor(background))
            if role == Qt.ForegroundRole:
                foreground = StandardDataService.get_by_id('complects_statuses', {'status_id': status_id})[3]
                return QBrush(QColor(foreground))
            if index.column() == 2:
                status = StandardDataService.get_by_id('complects_statuses', {'status_id': status_id})[1]
                return status if status else 'Ошибка!'
            if index.column() == 3:
                fusion = StandardDataService.get_by_id('fusions', {'fusion_id': fusion_id})[1]
                return fusion if fusion else 'Ошибка!'
            if index.column() == 9:
                direction = StandardDataService.get_by_id('directions', {'direction_id': direction_id})[1]
                return direction if direction else 'Ошибка!'
        return item.data(index.column())
    
    def realdata(self, index: QModelIndex, role: int) -> Any:
        if not index.isValid():
            return None
        if role != Qt.DisplayRole and role != Qt.EditRole and role != Qt.BackgroundRole and role != Qt.ForegroundRole:
            return None
        item = index.internalPointer()
        return item.data(index.column())

    def clear(self):
        self.beginResetModel()
        self.root_item.removeChildren(0, self.root_item.childCount())
        self.endResetModel()

    def setupModelData(self):
        if self.root_item.childCount():
            self.clear()
        data = OrderDataService.complects({'order_id': self.__order_id})
        for article in data:
            article_id, nomenclature = article
            self.appendRow([nomenclature, article_id, None, None, None, None, None, None, None, None], QModelIndex())

            # Получение индекса только что добавленной записи изделия
            parent = self.index(0, 0, QModelIndex())
            detail = data[article]            

            # Выполнение для всех деталей, связанных с заданной ведомостью
            for sub_line in detail:
                detail_id, fusion_id, name, l, w, d, amount, priority, direction_id, status_id = sub_line
                self.appendRow([name, detail_id, status_id, fusion_id, l, w, d, amount, priority, direction_id], parent)


class ProductInformationFilterProxyModel(QSortFilterProxyModel):

    def __init__(self, parent=None):
        super(ProductInformationFilterProxyModel, self).__init__(parent)
        self.product_id_filter = ''
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
            product_id = str(self.sourceModel().data(
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
                self.product_id_filter in product_id and \
                self.designtaion_filter in designation

    @Slot(str)
    def register(self, filter: str):
        self.product_id_filter = filter
        self.invalidateFilter()

    @Slot(str)
    def designation(self, filter: str):
        self.designtaion_filter = filter
        self.invalidateFilter()

    @Slot(str)
    def nomenclature(self, filter: str):
        self.nomenclature_filter = filter
        self.invalidateFilter()

    @Slot(bool)
    def rent(self, filter: str):
        if filter:
            self.rent_filter = 'Да'
        else:
            self.rent_filter = ''
        self.invalidateFilter()

    @Slot(str)
    def type(self, filter: str):
        if filter == 'Все изделия':
            filter = ''
        self.type_filter = filter
        self.invalidateFilter()


class ArticleInformationFilterProxyModel(QSortFilterProxyModel):

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
    def nomenclature(self, filter: str):
        self.nomenclature_filter = filter
        self.invalidateFilter()


class OrderComplectsFilterProxyModel(QSortFilterProxyModel):

    def filterAcceptsRow(self, sourceRow: int,
                         sourceParent: QModelIndex) -> bool:
        index = self.sourceModel().index(sourceRow, 0, sourceParent)
        if not index.parent().isValid():
            return self.sourceModel().data(
                self.sourceModel().index(sourceRow, 11, QModelIndex()),
                Qt.DisplayRole
            )
        else:
            return self.sourceModel().data(
                self.sourceModel().index(sourceRow, 11, index.parent()),
                Qt.DisplayRole
            )
        return False
