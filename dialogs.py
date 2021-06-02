from datetime import datetime
import logging
from PySide6.QtCore import Qt, Signal, QPointF, QModelIndex
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QDialog, QCompleter, QMessageBox, QHBoxLayout, QMenu,
    QGraphicsDropShadowEffect
)

from gui import (
    ui_add_product_dialog, ui_add_article_dialog, ui_add_detail_dialog,
    ui_finish_step_dialog, ui_add_order_dialog, ui_add_ingot_dialog
)
from service import (
    OrderDataService, ProductDataService, StandardDataService, IngotsDataService
)
from models import (
   ComplectsModel, ArticleInformationFilterProxyModel, IngotModel, NewOrderFilterProxyModel
)
from widgets import IngotSectionDelegate, Plate


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

        self.ui.register_number.setValidator(QIntValidator(self.ui.register_number))

        type_list = ProductDataService.type_list()
        product_completer = QCompleter(type_list, self)
        product_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.ui.product_type.setCompleter(product_completer)

        self.ui.add.clicked.connect(self.addProduct)
        self.ui.ok.clicked.connect(self.accept)
        self.ui.cancel.clicked.connect(self.reject)

    def addProduct(self):
        """Добавление данных о новой продукции в базу.
        
        Данные собираются с формы диалогового окна и проверяются на заполнение.
        """
        product_id = self.ui.register_number.text()
        product_type = self.ui.product_type.text()
        designation = self.ui.designation.text()

        # Если номер ведомости, тип и описание заполнены, то можно добавлять
        if product_id and product_type and designation:
            success = StandardDataService.save_record(
                'products', product_id=product_id, product_type=product_type, designation=designation
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
            QMessageBox.critical(
                self,
                'Ошибка добавления',
                'Все поля должны быть обязательно заполнены!',
                QMessageBox.Ok
            )


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

        self.ui.add.clicked.connect(self.addArticle)
        self.ui.ok.clicked.connect(self.accept)
        self.ui.cancel.clicked.connect(self.reject)

    def setRegister(self, value: str):
        """Установка данных о номере ведомости.

        :param value: Номер ведомости
        :type value: str
        """
        self.ui.register_number.setText(value)

    def setDesignation(self, value: str):
        """Установка данных об описании продукции.

        :param value: Описание продукции
        :type value: str
        """
        self.ui.designation.setText(value)

    def setType(self, value: str):
        """Установка данных о типе продукции.

        :param value: Тип продукции
        :type value: str
        """
        self.ui.product_type.setText(value)

    def addArticle(self):
        """Добавление данных о новом изделии в базу.
        
        Данные собираются с формы диалогового окна и проверяются на заполнение.
        """
        nomenclature = self.ui.nomenclature.text()
        rent = int(self.ui.rent.isChecked())
        product_id = int(self.ui.register_number.text())
        type = self.ui.product_type.text()

        # Если заполнена номенклатура и номер ведомости
        if nomenclature and product_id:
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
            QMessageBox.critical(
                self,
                'Ошибка добавления',
                'Все поля должны быть обязательно заполнены!',
                QMessageBox.Ok
            )


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
        self.setWindowTitle('Добавление детали')

        self.ui.add.clicked.connect(self.addDetail)
        self.ui.ok.clicked.connect(self.accept)
        self.ui.cancel.clicked.connect(self.reject)

    def setRegister(self, value: str):
        """Установка данных о номере ведомости.

        :param value: Номер ведомости
        :type value: str
        """
        self.ui.register_number.setText(value)

    def setDesignation(self, value: str):
        """Установка данных об описании продукции.

        :param value: Описание продукции
        :type value: str
        """
        self.ui.designation.setText(value)

    def setType(self, value: str):
        """Установка данных о типе продукции.

        :param value: Тип продукции
        :type value: str
        """
        self.ui.product_type.setText(value)

    def setDirectionsList(self, directions: list):
        """Установка данных о направлениях проката.

        :param directions: Список доступных направлений
        :type directions: list
        """
        self.directions_id = []
        self.directions_names = []
        for direction in directions:
            self.directions_id.append(direction[0])
            self.directions_names.append(direction[1])
        self.ui.directions.addItems(self.directions_names)

    def setFusionsList(self, fusions: list):
        """Установка данных о используемых сплавах.

        :param fusions: Список доступных сплавов
        :type fusions: list
        """
        self.fusions_id = []
        self.fusions_names = []
        for fusion in fusions:
            self.fusions_id.append(fusion[0])
            self.fusions_names.append(fusion[1])
        self.ui.fusions.addItems(self.fusions_names)

    def addDetail(self):
        """Добавление данных о новой заготовке в базу.
        
        Данные собираются с формы диалогового окна и проверяются на заполнение.
        """
        name = self.ui.name.text()
        product_id = int(self.ui.register_number.text())
        # В списке по соответствию находится ID записи используемого сплава
        fusion_id = self.fusions_id[self.ui.fusions.currentIndex()]
        height = self.ui.height.value()
        width = self.ui.width.value()
        depth = self.ui.depth.value()
        # В списке по соответствию находится ID записи направления проката
        direction_id = self.directions_id[self.ui.directions.currentIndex()]
        priority = self.ui.priority.value()
        amount = self.ui.amount.value()

        # Если имя, габаритные размеры и количество заполнены, то добавляем
        if name and height and width and depth and amount:
            success = StandardDataService.save_record(
                'details', name=name, product_id=product_id,
                fusion_id=fusion_id, height=height, width=width, depth=depth,
                amount=amount, priority=priority, direction_id=direction_id
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
            QMessageBox.critical(
                self,
                'Ошибка добавления',
                'Все поля должны быть обязательно заполнены!',
                QMessageBox.Ok
            )


class OrderDialog(QDialog):
    """Диалоговое окно добавления нового заказа.

    После добавления нового заказа не посылает сигнал с параметрами, т.к.
    главный сценарий использования окна включает добавление одного заказа и
    дальнейшую работу уже с ним, а не создание прочих заказов.
    """
    def __init__(self, parent):
        super(OrderDialog, self).__init__(parent)
        self.ui = ui_add_order_dialog.Ui_Dialog()
        self.ui.setupUi(self)

        # Иерархическая модель изделие->заготовки для формирования заказа
        # ID (int) - идентификатор конкретного изделия или заготовки
        # ADDED (bool) - статус добавления этой заготовки или изделия в заказ
        self.model = ComplectsModel([
            'Ведомость', 'Название', 'Аренда', 'Длина', 'Ширина',
            'Толщина', 'Количество', 'Приоритет', 'ID', 'ADDED'
        ])
        
        # Список выбранных слитков (точнее их идентификаторов)
        # self.ingots = []
        
        # Прокси-модель для поиска нужных изделий (фильтр по названию)
        self.search_proxy = ArticleInformationFilterProxyModel()
        self.search_proxy.setSourceModel(self.model)
        self.ui.treeView_1.setModel(self.search_proxy)

        # Прокси модель добавленных заготовок и изделий (фильтр по флагу ADDED)
        self.choice_proxy = NewOrderFilterProxyModel()
        self.choice_proxy.setSourceModel(self.model)
        self.ui.treeView_2.setModel(self.choice_proxy)

        for column in range(self.model.columnCount(QModelIndex())):
            self.ui.treeView_1.resizeColumnToContents(column)

        for i in range(3, 10):
            self.ui.treeView_1.setColumnHidden(i, True)
        for i in range(8, 10):
            self.ui.treeView_2.setColumnHidden(i, True)
        
        self.ingot_model = IngotModel()
        self.ingot_model.setupModelData()
        self.ingot_delegate = IngotSectionDelegate(self.ui.ingotsView)
        self.ui.ingotsView.setItemDelegate(self.ingot_delegate)
        self.ui.ingotsView.setModel(self.ingot_model)

        self.customContextMenuRequested.connect(self.showContextMenu)
        self.ui.searchName.textChanged.connect(self.search_proxy.setNomenclature)
        self.ui.add.clicked.connect(self.addOrder)
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
                    add.triggered.connect(self.addDetail)
                else:
                    add = menu.addAction('Добавить изделие целиком')
                    add.triggered.connect(self.addArticle)
        if self.ui.treeView_2.hasFocus():
            if self.model.rowCount(QModelIndex()):
                if self.ui.treeView_2.currentIndex().parent().isValid():
                    delete = menu.addAction('Убрать деталь')
                    delete.triggered.connect(self.removeDetail)
                else:
                    delete = menu.addAction('Убрать изделие целиком')
                    delete.triggered.connect(self.removeArticle)
        menu.exec_(self.mapToGlobal(point))

    def addArticle(self):
        index = self.search_proxy.mapToSource(self.ui.treeView_1.currentIndex())
        parent = self.model.parent(index)

        # HACK: если не перенести индекс на первую колонку, работать не будет
        index = self.model.index(index.row(), 0, parent)

        parent_state_index = self.model.index(index.row(), 9, parent)
        self.model.setData(parent_state_index, True, Qt.EditRole)

        for row in range(self.model.rowCount(index)):
            child_state_index = self.model.index(row, 9, index)
            self.model.setData(child_state_index, True, Qt.EditRole)

        for column in range(self.model.columnCount(QModelIndex())):
            self.ui.treeView_2.resizeColumnToContents(column)

    def addDetail(self):
        index = self.search_proxy.mapToSource(self.ui.treeView_1.currentIndex())
        parent = self.model.parent(index)

        # HACK: если не перенести индекс на первую колонку, работать не будет
        index = self.model.index(index.row(), 0, parent)

        child_state_index = self.model.index(index.row(), 9, parent)
        self.model.setData(child_state_index, True, Qt.EditRole)

        parent_state_index = self.model.index(parent.row(), 9, QModelIndex())
        self.model.setData(parent_state_index, True, Qt.EditRole)

        for column in range(self.model.columnCount(QModelIndex())):
            self.ui.treeView_2.resizeColumnToContents(column)

    def removeArticle(self):
        index = self.choice_proxy.mapToSource(self.ui.treeView_2.currentIndex())
        parent = self.model.parent(index)

        # HACK: если не перенести индекс на первую колонку, работать не будет
        index = self.model.index(index.row(), 0, parent)

        parent_state_index = self.model.index(index.row(), 9, parent)
        self.model.setData(parent_state_index, False, Qt.EditRole)

        # Если убирается изделие, то убираются и все его заготовки
        for row in range(self.model.rowCount(index)):
            child_state_index = self.model.index(row, 9, index)
            self.model.setData(child_state_index, False, Qt.EditRole)

    def removeDetail(self):
        index = self.choice_proxy.mapToSource(self.ui.treeView_2.currentIndex())
        parent = self.model.parent(index)

        # HACK: если не перенести индекс на первую колонку, работать не будет
        index = self.model.index(index.row(), 0, parent)

        # Если является последней убираемой заготовкой, то убрать и изделие
        child_state_index = self.model.index(index.row(), 9, parent)
        self.model.setData(child_state_index, False, Qt.EditRole)
        if not self.haveAcceptedRows(parent):
            row = parent.row()
            parent_state_index = self.model.index(row, 9, QModelIndex())
            self.model.setData(parent_state_index, False, Qt.EditRole)

    def haveAcceptedRows(self, index: QModelIndex) -> bool:
        """Проверка наличия другой выбранной заготовки в пределах изделия.

        :param index: Ссылка на проверяемую запись
        :type index: QModelIndex
        :return: Истина, если есть другие заготовки, и ложь в обратном случае
        :rtype: bool
        """
        rows_states = []
        for row in range(self.model.rowCount(index)):
            row_index = self.model.index(row, 9, index)
            rows_states.append(self.model.data(row_index, Qt.DisplayRole))
        return any(rows_states)

    def addOrder(self):
        """Добавление данных о новом заказе в базу.
        
        Данные собираются с формы диалогового окна и проверяются на заполнение.
        """
        # Имя и статус складирования заказа - основа записи в базе данных
        order_name = self.ui.orderName.text()
        selected_indexes = self.ui.ingotsView.selectedIndexes()

        # Если заполнено имя, выбран хотя бы один слиток и изделие
        if order_name and selected_indexes and self.choice_proxy.rowCount(QModelIndex()):
            success = StandardDataService.save_record(
                'orders', status_id=1, name=order_name, is_on_storage=0, date=datetime.today().strftime("%d_%m_%Y")
            )
            if success:
                order_id = OrderDataService.max_id()

                used_fusions = []
                for index in selected_indexes:
                    data_row = self.ingot_model.data(index, Qt.DisplayRole)
                    StandardDataService.update_record(
                        'ingots',
                        {'ingot_id': data_row['ingot_id']},
                        order_id=order_id
                    )
                    used_fusions.append(data_row['fusion_id'])

                # Добавляем записи о комплектации заказа в целом
                for row in range(self.choice_proxy.rowCount(QModelIndex())):
                    proxy_index = self.choice_proxy.index(row, 0, QModelIndex())
                    index = self.choice_proxy.mapToSource(proxy_index)

                    id_index = self.model.index(index.row(), 8, QModelIndex())
                    id_1 = self.model.data(id_index, Qt.DisplayRole)

                    # HACK: без этого работать не будет
                    index = self.model.index(index.row(), 0, QModelIndex())

                    # Добавляем записи о заготовках в заказе
                    for row in range(self.model.rowCount(index)):
                        id_index = self.model.index(row, 9, index)

                        if self.model.data(id_index, Qt.DisplayRole):
                            index_1 = self.model.index(row, 6, index)
                            amount = self.model.data(index_1, Qt.DisplayRole)
                            index_2 = self.model.index(row, 7, index)
                            priority = self.model.data(index_2, Qt.DisplayRole)
                            index_3 = self.model.index(row, 8, index)
                            id_2 = self.model.data(index_3, Qt.DisplayRole)

                            fusion_id = StandardDataService.get_by_id(
                                'details', {'detail_id': id_2})[2]
                            id_3 = 1 if fusion_id in used_fusions else 6
                            StandardDataService.save_record(
                                'complects', order_id=order_id, article_id=id_1,
                                detail_id=id_2, amount=amount, priority=priority,
                                status_id=id_3
                            )
                QMessageBox.information(
                    self,
                    f'Заказ {order_name}',
                    f'Заказ {order_name} был успешно добавлен в базу!',
                    QMessageBox.Ok
                )
                complects = OrderDataService.complects({'order_id': order_id})
                self.pack = {
                    'order_id': order_id,
                    'status_name': 'В работе',
                    'status_id': 1,
                    'order_name': order_name,
                    'current_depth': max([line[6] for pack in complects.values() for line in pack]),
                    'efficiency': 0.0,
                    'is_on_storage': 0,
                    'creation_date': datetime.today().strftime("%d_%m_%Y"),
                    'complects': complects,
                    'ingots': OrderDataService.ingots({'order_id': order_id}),
                    'detail_number': sum([line[2] for pack in complects.values() for line in pack]),
                    'article_number': len(complects),
                }
                self.accept()

                logging.info('Заказ %(name)s добавлен в базу.', {'name': order_name})
            else:
                QMessageBox.critical(
                    self,
                    'Ошибка добавления',
                    f'Заказ {order_name} не был добавлен в базу '
                    'из-за программной ошибки!',
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

    def getNewOrder(self):
        return self.pack


class NewIngotDialog (QDialog):

    def __init__(self, parent=None):
        super(NewIngotDialog, self).__init__(parent)
        self.ui = ui_add_ingot_dialog.Ui_Dialog()
        self.ui.setupUi(self)

        self.setWindowTitle('Добавление слитка')
        self.ui.add.clicked.connect(self.add)
        self.ui.cancel.clicked.connect(self.reject)

    def setFusionsList(self, fusions: list):
        self.fusions_id = []
        self.fusions_names = []
        for fusion in fusions:
            self.fusions_id.append(fusion[0])
            self.fusions_names.append(fusion[1])
        self.ui.fusion.addItems(self.fusions_names)

    def add(self):
        batch = self.ui.batch.text()
        height = self.ui.height.value()
        width = self.ui.width.value()
        depth = self.ui.depth.value()
        fusion_id = self.fusions_id[self.ui.fusion.currentIndex()]

        if batch and height and width and depth:
            success = StandardDataService.save_record(
                'ingots',
                fusion_id=fusion_id,
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
            QMessageBox.critical(
                self,
                'Ошибка добавления',
                'Все поля должны быть обязательно заполнены!',
                QMessageBox.Ok
            )
