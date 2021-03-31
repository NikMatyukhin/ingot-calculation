import application_rc

from typing import NoReturn, List, Any

from PySide6.QtCore import Qt, Signal, QPointF, QModelIndex
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (QApplication, QDialog, QAbstractItemView,
                               QTableWidgetItem, QCompleter, QMessageBox,
                               QMenu)

from gui import (ui_catalog, ui_add_product_dialog, ui_add_article_dialog,
                 ui_add_detail_dialog)
from service import (ProductDataService, ArticleDataService,
                     StandardDataService, FusionDataService, DetailDataService)
from models import CatalogModel, ProductInformationFilterProxyModel
from dialogs import ProductDialog, ArticleDialog, DetailDialog


class Catalog (QDialog):

    def __init__(self, parent=None):
        super(Catalog, self).__init__(parent)
        self.ui = ui_catalog.Ui_Form()
        self.ui.setupUi(self)

        self.setWindowFlags(Qt.Window)

        self.ui.type.addItems(
            ['Все изделия'] + ProductDataService.type_list()
        )

        self.model = CatalogModel(
            ['Ведомость', 'Тип', 'Название', 'Аренда', 'ID']
        )
        self.model.dataChanged.connect(self.updateRecord)
        self.proxy = ProductInformationFilterProxyModel()
        self.proxy.setSourceModel(self.model)

        self.ui.productsView.setModel(self.proxy)
        self.ui.productsView.resizeColumnToContents(0)
        self.ui.productsView.resizeColumnToContents(1)
        self.ui.productsView.resizeColumnToContents(2)
        self.ui.productsView.setColumnHidden(1, True)
        self.ui.productsView.setColumnHidden(4, True)
        self.ui.productsView.clicked.connect(self.showDetailsList)

        self.ui.detailsView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.detailsView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.detailsView.itemSelectionChanged.connect(self.showInformation)

        self.ui.register_number.textChanged.connect(self.proxy.setRegister)
        self.ui.designation.textChanged.connect(self.proxy.setDesignation)
        self.ui.nomenclature.textChanged.connect(self.proxy.setNomenclature)
        self.ui.type.currentTextChanged.connect(self.proxy.setType)
        self.ui.rent.stateChanged.connect(self.proxy.setRent)

        self.ui.newProduct.clicked.connect(self.openProductDialog)
        self.ui.newArticle.clicked.connect(self.openArticleDialog)
        self.ui.newDetail.clicked.connect(self.openDetailDialog)
        # TODO: дописать логику кнопки с новой картинкой для детали
        self.customContextMenuRequested.connect(self.showContextMenu)

    def showDetailsList(self, current_index: QModelIndex) -> NoReturn:
        self.ui.detailsView.clearContents()
        self.ui.detailsView.setRowCount(0)

        index = self.proxy.mapToSource(current_index)
        parent = self.model.parent(index)

        if not parent.isValid():
            register_index = self.model.index(index.row(), 0, parent)
            id = self.model.data(register_index, Qt.DisplayRole)
            details_list = DetailDataService.details_list({'register_id': id})

            for detail in details_list:
                self.ui.detailsView.insertRow(self.ui.detailsView.rowCount())

                for column, data in enumerate(detail):
                    data = str(data) if data else '-'
                    item = QTableWidgetItem(str(data))
                    row = self.ui.detailsView.rowCount() - 1
                    self.ui.detailsView.setItem(row, column, item)

        for column in range(8):
            self.ui.detailsView.resizeColumnToContents(column)
        self.ui.detailsView.hideColumn(8)

    def showInformation(self) -> NoReturn:

        selected_items = self.ui.detailsView.selectedItems()

        if len(selected_items) < 6:
            self.ui.detailTitle.setText('Название детали: ...')
            self.ui.detailInfo.setText('Описание детали...')
        else:
            name = selected_items[0].data(Qt.DisplayRole)
            fusion = selected_items[1].data(Qt.DisplayRole)
            height = selected_items[2].data(Qt.DisplayRole)
            width = selected_items[3].data(Qt.DisplayRole)
            depth = selected_items[4].data(Qt.DisplayRole)
            direction = selected_items[7].data(Qt.DisplayRole)

            self.ui.detailTitle.setText('Название детали: ' + name)
            information = str(
                f'<br><b>Сплав</b>: деталь изготавливается из слитка {fusion}'
                f'<br><br><b>Размеры детали</b>: {height}x{width}x{depth} мм'
                f'<br><br><b>Направление проката детали</b>: {direction}')
            self.ui.detailInfo.setText(information)

    def showContextMenu(self, point: QPointF) -> NoReturn:
        menu = QMenu()

        if self.ui.productsView.hasFocus():
            if self.model.rowCount(QModelIndex()):
                if self.ui.productsView.currentIndex().parent().isValid():
                    delete = menu.addAction('Удалить артикул')
                    delete.triggered.connect(self.deleteArticle)
                else:
                    add = menu.addAction('Добавить артикул')
                    delete = menu.addAction('Удалить изделие')
                    add.triggered.connect(self.openArticleDialog)
                    delete.triggered.connect(self.deleteProduct)
        elif self.ui.detailsView.hasFocus():
            add = menu.addAction('Добавить деталь')
            delete = menu.addAction('Удалить деталь')
            add.triggered.connect(self.openDetailDialog)
            delete.triggered.connect(self.deleteDetail)

        menu.exec_(self.mapToGlobal(point))

    def openProductDialog(self) -> NoReturn:
        window = ProductDialog(self)
        window.recordSavedSuccess.connect(self.addProduct)

        window.exec_()

    def openArticleDialog(self) -> NoReturn:
        window = ArticleDialog(self)
        window.recordSavedSuccess.connect(self.addArticle)

        index = self.proxy.mapToSource(self.ui.productsView.currentIndex())
        if not index.isValid():
            return False

        register_index = self.model.index(index.row(), 0, QModelIndex())
        type_index = self.model.index(index.row(), 1, QModelIndex())
        designation_index = self.model.index(index.row(), 2, QModelIndex())

        register = self.model.data(register_index, Qt.DisplayRole)
        type = self.model.data(type_index, Qt.DisplayRole)
        designation = self.model.data(designation_index, Qt.DisplayRole)

        window.setRegister(register)
        window.setDesignation(designation)
        window.setType(type)

        window.exec_()

    def openDetailDialog(self) -> NoReturn:
        window = DetailDialog(self)
        window.recordSavedSuccess.connect(self.addDetail)

        index = self.proxy.mapToSource(self.ui.productsView.currentIndex())
        if not index.isValid():
            return False

        register_index = self.model.index(index.row(), 0, QModelIndex())
        type_index = self.model.index(index.row(), 1, QModelIndex())
        designation_index = self.model.index(index.row(), 2, QModelIndex())

        register = self.model.data(register_index, Qt.DisplayRole)
        type = self.model.data(type_index, Qt.DisplayRole)
        designation = self.model.data(designation_index, Qt.DisplayRole)
        fusions_list = FusionDataService.fusions_list()

        window.setRegister(register)
        window.setDesignation(designation)
        window.setFusionsList(fusions_list)
        window.setType(type)

        window.exec_()

    def updateRecord(self, index: QModelIndex, temp: QModelIndex,
                     roles: List[int]) -> NoReturn:

        parent = self.model.parent(index)
        if parent.isValid():
            self.updateArticle(index, index, roles)
        else:
            self.updateProduct(index, index, roles)

    def updateProduct(self, index: QModelIndex, temp: QModelIndex,
                      roles: List[int]) -> NoReturn:

        parent = self.model.parent(index)
        register_index = self.model.index(index.row(), 0, parent)
        designation_index = self.model.index(index.row(), 2, parent)

        register = self.model.data(register_index, Qt.DisplayRole)
        designation = self.model.data(designation_index, Qt.DisplayRole)

        success = StandardDataService.update_record(
            'products',
            {'register_number': register},
            designation=designation
        )

        if not success:
            QMessageBox.critical(
                self,
                'Ошибка обновления',
                f'Продукция {register}\nне была обновлена в базе '
                'из-за программной ошибки!',
                QMessageBox.Ok
            )

    def updateArticle(self, index: QModelIndex, temp: QModelIndex,
                      roles: List[int]) -> NoReturn:

        parent = self.model.parent(index)
        nomen_index = self.model.index(index.row(), 2, parent)
        rent_index = self.model.index(index.row(), 3, parent)
        article_index = self.model.index(index.row(), 4, parent)

        nomenclature = self.model.data(nomen_index, Qt.DisplayRole)
        rent = ['Нет', 'Да'].index(self.model.data(rent_index, Qt.DisplayRole))
        article = self.model.data(article_index, Qt.DisplayRole)

        success = StandardDataService.update_record(
            'articles',
            {'article_id': article},
            nomenclature=nomenclature,
            rent=rent
        )

        if not success:
            QMessageBox.critical(
                self,
                'Ошибка обновления',
                f'Изделие {nomenclature}\nне было обновлено в базе '
                'из-за программной ошибки!',
                QMessageBox.Ok
            )

    def updateDetail(self, index: QModelIndex, temp: QModelIndex,
                     roles: List[int]) -> NoReturn:
        # TODO: Есть проблемы. Оставлю до лучших времён рефакторинга, аминь.
        pass

    def addProduct(self, data: List[Any]) -> NoReturn:

        key, type, designation = data
        self.model.appendRow([key, type, designation]+[None]*2, QModelIndex())

    def addArticle(self, data: List[Any]) -> NoReturn:

        parent = self.proxy.mapToSource(self.ui.productsView.currentIndex())

        key, type, nomenclature, rent = data
        id = ArticleDataService.get_by_fields(
            'articles',
            register_id=key,
            nomenclature=nomenclature,
            rent=rent
        )
        rent = ['Нет', 'Да'][rent]
        self.model.appendRow([None, type, nomenclature, rent, id], parent)
        self.proxy.invalidate()

    def addDetail(self, data: List[Any]) -> NoReturn:

        self.ui.detailsView.insertRow(self.ui.detailsView.rowCount())

        for column, data in enumerate(data):
            data = str(data) if data else '-'
            row = self.ui.detailsView.rowCount() - 1
            item = QTableWidgetItem(str(data))
            self.ui.detailsView.setItem(row, column, item)

    def deleteProduct(self) -> NoReturn:
        index = self.proxy.mapToSource(self.ui.productsView.currentIndex())
        id_index = self.model.index(index.row(), 0, QModelIndex())
        id = self.model.data(id_index, Qt.DisplayRole)

        success = StandardDataService.delete_by_id(
            'products',
            {'register_number': id}
        )

        if success:
            self.model.removeRows(index.row(), 1, QModelIndex())
        else:
            QMessageBox.critical(
                self,
                'Ошибка удаления',
                'Продукция не была удалена из базы\n'
                'из-за программной ошибки!',
                QMessageBox.Ok
            )

    def deleteArticle(self) -> NoReturn:
        index = self.proxy.mapToSource(self.ui.productsView.currentIndex())
        parent = self.model.parent(index)
        id_index = self.model.index(index.row(), 4, parent)
        id = self.model.data(id_index, Qt.DisplayRole)

        success = StandardDataService.delete_by_id(
            'articles',
            {'article_id': id}
        )

        if success:
            self.model.removeRows(index.row(), 1, parent)
        else:
            QMessageBox.critical(
                self,
                'Ошибка удаления',
                'Изделие не было удалено из базы\n'
                'из-за программной ошибки!',
                QMessageBox.Ok
            )

    def deleteDetail(self) -> NoReturn:
        row = self.ui.detailsView.currentRow()
        id = self.ui.detailsView.item(row, 8).data(Qt.DisplayRole)

        success = StandardDataService.delete_by_id(
            'details',
            {'detail_id': id}
        )

        if success:
            self.ui.detailsView.removeRow(row)
        else:
            QMessageBox.critical(
                self,
                'Ошибка удаления',
                'Деталь не была удалена из базы\n'
                'из-за программной ошибки!',
                QMessageBox.Ok
            )


if __name__ == '__main__':
    application = QApplication()

    window = Catalog()
    window.show()

    application.exec_()
