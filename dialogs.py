from typing import NoReturn

from PySide6.QtCore import Qt, Signal, QPointF, QModelIndex
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (QDialog, QCompleter, QMessageBox, QHBoxLayout,
                               QMenu)

from gui import (ui_add_product_dialog, ui_add_article_dialog,
                 ui_add_detail_dialog, ui_finish_step_dialog,
                 ui_add_order_dialog)
from service import ProductDataService, StandardDataService, IngotsDataService
from models import (ComplectsModel, ArticleInformationFilterProxyModel,
                    NewOrderFilterProxyModel)
from plate import Plate


class ProductDialog (QDialog):

    recordSavedSuccess = Signal(list)

    def __init__(self, parent):
        super(ProductDialog, self).__init__(parent)
        self.ui = ui_add_product_dialog.Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.register_number.setValidator(
            QIntValidator(self.ui.register_number))

        type_list = ProductDataService.type_list()
        product_completer = QCompleter(type_list, self)
        product_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.ui.product_type.setCompleter(product_completer)

        self.ui.add.clicked.connect(self.add)
        self.ui.ok.clicked.connect(self.accept)
        self.ui.cancel.clicked.connect(self.reject)

    def add(self) -> NoReturn:
        register_number = self.ui.register_number.text()
        product_type = self.ui.product_type.text()
        designation = self.ui.designation.text()

        if register_number and product_type and designation:
            success = StandardDataService.save_record(
                'products',
                register_number=register_number,
                product_type=product_type,
                designation=designation
            )

            if success:
                QMessageBox.information(
                    self,
                    f'Продукция {register_number}',
                    f'Продукция с номером ведомости №{register_number}\n'
                    'успешно добавлена!',
                    QMessageBox.Ok
                )
                self.recordSavedSuccess.emit([
                    register_number,
                    product_type,
                    designation
                ])
            else:
                QMessageBox.critical(
                    self,
                    'Ошибка добавления',
                    f'Продукция с номером ведомости №{register_number}\n'
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


class ArticleDialog (QDialog):

    recordSavedSuccess = Signal(list)

    def __init__(self, parent):
        super(ArticleDialog, self).__init__(parent)
        self.ui = ui_add_article_dialog.Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.add.clicked.connect(self.add)
        self.ui.ok.clicked.connect(self.accept)
        self.ui.cancel.clicked.connect(self.reject)

    def setRegister(self, value: str) -> NoReturn:
        self.ui.register_number.setText(value)

    def setDesignation(self, value: str) -> NoReturn:
        self.ui.designation.setText(value)

    def setType(self, value: str) -> NoReturn:
        self.ui.product_type.setText(value)

    def add(self) -> NoReturn:
        nomenclature = self.ui.nomenclature.text()
        rent = int(self.ui.rent.isChecked())
        register_id = int(self.ui.register_number.text())
        type = self.ui.product_type.text()

        if nomenclature and register_id:
            success = StandardDataService.save_record(
                'articles',
                register_id=register_id,
                nomenclature=nomenclature,
                rent=rent
            )

            if success:
                QMessageBox.information(
                    self,
                    f'Продукция {register_id}',
                    f'Изделие {nomenclature}\nуспешно добавлено!',
                    QMessageBox.Ok
                )
                self.recordSavedSuccess.emit([
                    register_id,
                    type,
                    nomenclature,
                    rent
                ])
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


class DetailDialog (QDialog):

    recordSavedSuccess = Signal(list)

    def __init__(self, parent):
        super(DetailDialog, self).__init__(parent)
        self.ui = ui_add_detail_dialog.Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.add.clicked.connect(self.add)
        self.ui.ok.clicked.connect(self.accept)
        self.ui.cancel.clicked.connect(self.reject)

    def setRegister(self, value: str) -> NoReturn:
        self.ui.register_number.setText(value)

    def setDesignation(self, value: str) -> NoReturn:
        self.ui.designation.setText(value)

    def setType(self, value: str) -> NoReturn:
        self.ui.product_type.setText(value)

    def setFusionsList(self, fusions: list) -> NoReturn:
        self.fusions_id = []
        self.fusions_names = []
        for fusion in fusions:
            self.fusions_id.append(fusion[0])
            self.fusions_names.append(fusion[1])
        self.ui.fusions.addItems(self.fusions_names)

    def add(self) -> NoReturn:
        name = self.ui.name.text()
        register_id = int(self.ui.register_number.text())
        fusion_id = self.fusions_id[self.ui.fusions.currentIndex()]
        height = self.ui.height.value()
        width = self.ui.width.value()
        depth = self.ui.depth.value()
        # TODO: направления проката не подгружаются из базы, а вшиты в код
        direction_id = self.ui.direction.currentIndex()
        priority = self.ui.priority.value()
        amount = self.ui.amount.value()

        if name and height and width and depth and amount:
            # TODO: связать ID направления проката с названием, как у сплавов
            success = StandardDataService.save_record(
                'details',
                name=name,
                register_id=register_id,
                fusion_id=fusion_id,
                height=height,
                width=width,
                depth=depth,
                amount=amount,
                priority=priority,
                direction_id=direction_id+1
            )

            if success:
                QMessageBox.information(
                    self,
                    f'Продукция {register_id}',
                    f'Деталь {name}\nуспешно добавлена!',
                    QMessageBox.Ok
                )
                self.recordSavedSuccess.emit([
                    name,
                    self.ui.fusions.currentText(),
                    height,
                    width,
                    depth,
                    amount,
                    priority,
                    self.ui.direction.currentText(),
                    register_id
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


class NewOrderDialog(QDialog):

    def __init__(self, parent):
        super(NewOrderDialog, self).__init__(parent)
        self.ui = ui_add_order_dialog.Ui_Dialog()
        self.ui.setupUi(self)

        self.model = ComplectsModel([
                'Ведомость', 'Название', 'Аренда', 'Количество',
                'Приоритет', 'ID', 'ADDED'
        ])
        self.proxy_1 = ArticleInformationFilterProxyModel()
        self.proxy_1.setSourceModel(self.model)
        self.ui.treeView_1.setModel(self.proxy_1)

        self.proxy_2 = NewOrderFilterProxyModel()
        self.proxy_2.setSourceModel(self.model)
        self.ui.treeView_2.setModel(self.proxy_2)

        for column in range(self.model.columnCount(QModelIndex())):
            self.ui.treeView_1.resizeColumnToContents(column)

        self.ui.treeView_1.setColumnHidden(3, True)
        self.ui.treeView_1.setColumnHidden(4, True)
        self.ui.treeView_1.setColumnHidden(5, True)
        self.ui.treeView_1.setColumnHidden(6, True)

        self.ui.treeView_2.setColumnHidden(5, True)
        self.ui.treeView_2.setColumnHidden(6, True)

        ingots_layout = QHBoxLayout()
        self.ingots = []
        for ingot in IngotsDataService.vacancy_ingots():
            ingot_plate = Plate(ingot[0], ingot[1], ingot[2], ingot[3:],
                                is_selected=False)
            ingot_plate.checked.connect(self.addIngot)
            ingots_layout.addWidget(ingot_plate)
        ingots_layout.setContentsMargins(0, 0, 0, 0)
        ingots_layout.setSpacing(0)
        ingots_layout.addStretch()
        self.ui.scrollAreaWidgetContents.setLayout(ingots_layout)

        self.customContextMenuRequested.connect(self.show_context_menu)
        self.ui.searchName.textChanged.connect(self.proxy_1.setNomenclature)
        self.ui.add.clicked.connect(self.addOrder)
        self.ui.cancel.clicked.connect(self.reject)

    def show_context_menu(self, point: QPointF):

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

    def addIngot(self, checked: bool) -> NoReturn:
        choosen_plate = self.sender()
        id = choosen_plate.getID()
        if id in self.ingots:
            self.ingots.remove(id)
        else:
            self.ingots.append(id)

    def addArticle(self) -> NoReturn:

        index = self.proxy_1.mapToSource(self.ui.treeView_1.currentIndex())
        parent = self.model.parent(index)

        # TODO: если не перенести индекс на первую колонку, работать не будет
        index = self.model.index(index.row(), 0, parent)

        parent_state_index = self.model.index(index.row(), 6, parent)
        self.model.setData(parent_state_index, True, Qt.EditRole)

        for row in range(self.model.rowCount(index)):
            child_state_index = self.model.index(row, 6, index)
            self.model.setData(child_state_index, True, Qt.EditRole)

        for column in range(self.model.columnCount(QModelIndex())):
            self.ui.treeView_2.resizeColumnToContents(column)

    def addDetail(self) -> NoReturn:

        index = self.proxy_1.mapToSource(self.ui.treeView_1.currentIndex())
        parent = self.model.parent(index)

        # TODO: если не перенести индекс на первую колонку, работать не будет
        index = self.model.index(index.row(), 0, parent)

        child_state_index = self.model.index(index.row(), 6, parent)
        self.model.setData(child_state_index, True, Qt.EditRole)

        parent_state_index = self.model.index(parent.row(), 6, QModelIndex())
        self.model.setData(parent_state_index, True, Qt.EditRole)

        for column in range(self.model.columnCount(QModelIndex())):
            self.ui.treeView_2.resizeColumnToContents(column)

    def removeArticle(self) -> NoReturn:

        index = self.proxy_2.mapToSource(self.ui.treeView_2.currentIndex())
        parent = self.model.parent(index)

        # TODO: если не перенести индекс на первую колонку, работать не будет
        index = self.model.index(index.row(), 0, parent)

        parent_state_index = self.model.index(index.row(), 6, parent)
        self.model.setData(parent_state_index, False, Qt.EditRole)

        for row in range(self.model.rowCount(index)):
            child_state_index = self.model.index(row, 6, index)
            self.model.setData(child_state_index, False, Qt.EditRole)

    def removeDetail(self) -> NoReturn:

        index = self.proxy_2.mapToSource(self.ui.treeView_2.currentIndex())
        parent = self.model.parent(index)

        # TODO: если не перенести индекс на первую колонку, работать не будет
        index = self.model.index(index.row(), 0, parent)

        child_state_index = self.model.index(index.row(), 6, parent)
        self.model.setData(child_state_index, False, Qt.EditRole)
        if not self.haveAcceptedRows(parent):
            row = parent.row()
            parent_state_index = self.model.index(row, 6, QModelIndex())
            self.model.setData(parent_state_index, False, Qt.EditRole)

    def haveAcceptedRows(self, index: QModelIndex) -> bool:

        rows_states = []
        for row in range(self.model.rowCount(index)):
            row_index = self.model.index(row, 6, index)
            rows_states.append(self.model.data(row_index, Qt.DisplayRole))
        return any(rows_states)

    def addOrder(self) -> NoReturn:

        name = self.ui.orderName.text()
        on_storage = int(self.ui.storage.isChecked())

        if name:
            success = StandardDataService.save_record(
                'orders',
                status_id=2,
                name=name,
                is_on_storage=on_storage
            )
            success = True
            if success:
                order_id = StandardDataService.get_by_fields(
                    'orders',
                    status_id=1,
                    name=name,
                    is_on_storage=on_storage
                )[0][0]
                order_amount = 0
                complect = []
                max_depth = -1
                for row in range(self.proxy_2.rowCount(QModelIndex())):
                    proxy_index = self.proxy_2.index(row, 0, QModelIndex())
                    index = self.proxy_2.mapToSource(proxy_index)

                    id_index = self.model.index(index.row(), 5, QModelIndex())
                    id_1 = self.model.data(id_index, Qt.DisplayRole)
                    order_amount += 1

                    # TODO: без этого работать не будет
                    index = self.model.index(index.row(), 0, QModelIndex())

                    for row in range(self.model.rowCount(index)):
                        id_index = self.model.index(row, 6, index)

                        if self.model.data(id_index, Qt.DisplayRole):
                            index_1 = self.model.index(row, 3, index)
                            amount = self.model.data(index_1, Qt.DisplayRole)
                            index_2 = self.model.index(row, 4, index)
                            priority = self.model.data(index_2, Qt.DisplayRole)
                            index_3 = self.model.index(row, 5, index)
                            id_2 = self.model.data(index_3, Qt.DisplayRole)

                            max_depth = max(DetailDataService.detail_depth(
                                {'detail_id': id_2}), max_depth)

                            StandardDataService.save_record(
                                'complects',
                                order_id=order_id,
                                article_id=id_1,
                                detail_id=id_2,
                                amount=amount,
                                priority=priority
                            )
                    for ingot in self.ingots:
                        StandardDataService.update_record(
                            'ingots',
                            {'ingot_id': ingot},
                            order_id=order_id
                        )
                QMessageBox.information(
                    self,
                    f'Заказ {name}',
                    f'Заказ {name} был успешно добавлен в базу!',
                    QMessageBox.Ok
                )
                self.pack = [
                    order_id,
                    name,
                    order_amount,
                    'В работе',
                    max_depth,
                    None
                ]
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    'Ошибка добавления',
                    f'Заказ {name} не был добавлен в базу '
                    'из-за программной ошибки!',
                    QMessageBox.Ok
                )
        else:
            QMessageBox.critical(
                self,
                'Ошибка добавления',
                'Поле названия заказа обязательно должно быть заполнено!',
                QMessageBox.Ok
            )

    def getNewOrder(self):
        return self.pack


class CloseOrderDialog (QDialog):

    def __init__(self, parent=None):
        super(CloseOrderDialog, self).__init__(parent)
        self.ui = ui_finish_step_dialog.Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.finish.clicked.connect(self.accept)
        self.ui.cancel.clicked.connect(self.reject)
