import application_rc

from typing import List, Any
from operator import itemgetter

from PyQt5.QtCore import Qt, QPointF, QModelIndex
from PyQt5.QtWidgets import (
    QApplication, QDialog, QTableWidgetItem, QMessageBox, QMenu, QTableWidget
)

from gui import ui_catalog
from service import (
    ProductDataService, ArticleDataService, StandardDataService, 
    DetailDataService
)
from models import CatalogModel, ProductInformationFilterProxyModel
from dialogs import ProductDialog, ArticleDialog, DetailDialog
from widgets import ListValuesDelegate


class Catalog(QDialog):

    def __init__(self, parent=None):
        super(Catalog, self).__init__(parent)
        self.ui = ui_catalog.Ui_Form()
        self.ui.setupUi(self)

        self.setWindowFlags(Qt.Window)

        self.ui.type.addItems(
            ['Все изделия'] + ProductDataService.type_list()
        )
        self.directions_list = StandardDataService.get_table('directions')
        self.directions_id = list(map(itemgetter(0), self.directions_list))
        self.directions_names = list(map(itemgetter(1), self.directions_list))
        self.fusions_list = StandardDataService.get_table('fusions')
        self.fusions_id = list(map(itemgetter(0), self.fusions_list))
        self.fusions_names = list(map(itemgetter(1), self.fusions_list))

        self.model = CatalogModel(
            ['Ведомость', 'Тип', 'Название', 'Аренда', 'ID']
        )
        self.model.dataChanged.connect(self.update_record_filter)
        self.proxy = ProductInformationFilterProxyModel()
        self.proxy.setSourceModel(self.model)

        self.ui.productsView.setModel(self.proxy)
        self.ui.productsView.resizeColumnToContents(0)
        self.ui.productsView.resizeColumnToContents(1)
        self.ui.productsView.resizeColumnToContents(2)
        self.ui.productsView.setColumnHidden(1, True)
        self.ui.productsView.setColumnHidden(4, True)
        self.ui.productsView.clicked.connect(self.show_details)

        self.ui.detailsView.itemSelectionChanged.connect(self.show_details_information)
        self.ui.detailsView.itemChanged.connect(self.update_detail)
        self.ui.detailsView.hideColumn(8)

        self.ui.register_number.textChanged.connect(self.proxy.register)
        self.ui.designation.textChanged.connect(self.proxy.designation)
        self.ui.nomenclature.textChanged.connect(self.proxy.nomenclature)
        self.ui.type.currentTextChanged.connect(self.proxy.type)
        self.ui.rent.stateChanged.connect(self.proxy.rent)

        self.ui.newProduct.clicked.connect(self.open_product_dialog)
        self.ui.newArticle.clicked.connect(self.open_article_dialog)
        self.ui.newDetail.clicked.connect(self.open_detail_dialog)

        # TODO: дописать логику кнопки с новой картинкой для детали
        self.customContextMenuRequested.connect(self.showContextMenu)

    def show_details(self, current_index: QModelIndex):
        view: QTableWidget = self.ui.detailsView
        view.clearContents()
        view.setRowCount(0)

        index = self.proxy.mapToSource(current_index)
        parent = self.model.parent(index)

        self.direction_delegate = ListValuesDelegate(self.directions_names)
        self.fusion_delegate = ListValuesDelegate(self.fusions_names)
        view.setItemDelegateForColumn(1, self.fusion_delegate)
        view.setItemDelegateForColumn(7, self.direction_delegate)

        if not parent.isValid():
            product_id_index = self.model.index(index.row(), 0, parent)
            id = self.model.data(product_id_index, Qt.DisplayRole)
            details_list = DetailDataService.details_list({'product_id': id})

            for detail in details_list:
                view.insertRow(view.rowCount())

                for column, data in enumerate(detail):
                    data = str(data) if data else '-'
                    item = QTableWidgetItem(str(data))
                    row = view.rowCount() - 1
                    view.setItem(row, column, item)

        for column in [0, 2, 3, 4, 5, 6]:
            view.resizeColumnToContents(column)

    def show_details_information(self):
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

    def showContextMenu(self, point: QPointF):
        """Метод вызова контекстного меню.

        Отвечает за добавление и удаление заготовок и изделий.

        :param point: Точка выхова контекстного меню
        :type point: QPointF
        """
        menu = QMenu()

        if self.ui.productsView.hasFocus():
            if self.model.rowCount(QModelIndex()):
                if self.ui.productsView.currentIndex().parent().isValid():
                    delete = menu.addAction('Удалить артикул')
                    delete.triggered.connect(self.confirm_article_removing)
                else:
                    add = menu.addAction('Добавить артикул')
                    delete = menu.addAction('Удалить изделие')
                    add.triggered.connect(self.open_article_dialog)
                    delete.triggered.connect(self.confirm_product_removing)
        elif self.ui.detailsView.hasFocus():
            add = menu.addAction('Добавить деталь')
            delete = menu.addAction('Удалить деталь')
            add.triggered.connect(self.open_detail_dialog)
            delete.triggered.connect(self.confirm_detail_removing)

        menu.exec_(self.mapToGlobal(point))

    def open_product_dialog(self):
        window = ProductDialog(self)
        window.recordSavedSuccess.connect(self.confirm_product_adding)

        window.exec_()

    def open_article_dialog(self):
        window = ArticleDialog(self)
        window.recordSavedSuccess.connect(self.confirm_article_adding)

        index = self.proxy.mapToSource(self.ui.productsView.currentIndex())
        if not index.isValid():
            return False

        product_id_index = self.model.index(index.row(), 0, QModelIndex())
        type_index = self.model.index(index.row(), 1, QModelIndex())
        designation_index = self.model.index(index.row(), 2, QModelIndex())

        product_id = self.model.data(product_id_index, Qt.DisplayRole)
        type = self.model.data(type_index, Qt.DisplayRole)
        designation = self.model.data(designation_index, Qt.DisplayRole)

        window.set_title_data(product_id, designation, type)

        window.exec_()

    def open_detail_dialog(self):
        window = DetailDialog(self)
        window.recordSavedSuccess.connect(self.confirm_detail_adding)

        index = self.proxy.mapToSource(self.ui.productsView.currentIndex())
        if not index.isValid():
            return False

        product_id_index = self.model.index(index.row(), 0, QModelIndex())
        type_index = self.model.index(index.row(), 1, QModelIndex())
        designation_index = self.model.index(index.row(), 2, QModelIndex())

        product_id = self.model.data(product_id_index, Qt.DisplayRole)
        type = self.model.data(type_index, Qt.DisplayRole)
        designation = self.model.data(designation_index, Qt.DisplayRole)

        window.set_title_data(product_id, designation, type)

        window.exec_()

    def update_record_filter(self, index: QModelIndex, temp: QModelIndex,
                     roles: List[int]):
        parent = self.model.parent(index)
        if parent.isValid():
            self.update_article(index, index, roles)
        else:
            self.update_product(index, index, roles)

    def update_product(self, index: QModelIndex, temp: QModelIndex,
                      roles: List[int]):
        parent = self.model.parent(index)
        product_id_index = self.model.index(index.row(), 0, parent)
        designation_index = self.model.index(index.row(), 2, parent)

        product_id = self.model.data(product_id_index, Qt.DisplayRole)
        designation = self.model.data(designation_index, Qt.DisplayRole)

        success = StandardDataService.update_record(
            'products',
            {'product_id': product_id},
            designation=designation
        )

        if not success:
            QMessageBox.critical(
                self,
                'Ошибка обновления',
                f'Продукция {product_id}\nне была обновлена в базе '
                'из-за программной ошибки!',
                QMessageBox.Ok
            )

    def update_article(self, index: QModelIndex, temp: QModelIndex,
                      roles: List[int]):
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

    def update_detail(self, it: QTableWidgetItem):
        id_item = self.ui.detailsView.item(it.row(), 8)
        if id_item:
            row, column, data = it.row(), it.column(), it.data(Qt.DisplayRole)
            id = id_item.data(Qt.DisplayRole)
            if column == 0:
                success = StandardDataService.update_record(
                    'details',
                    {'detail_id': id},
                    name=data
                )
            elif column == 1:
                success = StandardDataService.update_record(
                    'details',
                    {'detail_id': id},
                    fusion_id=self.fusions_id[self.fusions_names.index(data)]
                )
            elif column == 2:
                success = StandardDataService.update_record(
                    'details',
                    {'detail_id': id},
                    height=int(data)
                )
            elif column == 3:
                success = StandardDataService.update_record(
                    'details',
                    {'detail_id': id},
                    width=int(data)
                )
            elif column == 4:
                success = StandardDataService.update_record(
                    'details',
                    {'detail_id': id},
                    depth=float(data)
                )
            elif column == 5:
                success = StandardDataService.update_record(
                    'details',
                    {'detail_id': id},
                    amount=int(data)
                )
            elif column == 6:
                success = StandardDataService.update_record(
                    'details',
                    {'detail_id': id},
                    priority=int(data)
                )
            elif column == 7:
                success = StandardDataService.update_record(
                    'details',
                    {'detail_id': id},
                    direction_id=self.directions_id[
                        self.directions_names.index(data)]
                )

    def confirm_product_adding(self, data: List[Any]):
        key, type, designation = data
        self.model.appendRow([key, type, designation]+[None]*2, QModelIndex())

    def confirm_article_adding(self, data: List[Any]):
        parent = self.proxy.mapToSource(self.ui.productsView.currentIndex())

        key, type, nomenclature, rent = data
        id = ArticleDataService.get_by_fields(
            'articles',
            product_id=key,
            nomenclature=nomenclature,
            rent=rent
        )
        rent = ['Нет', 'Да'][rent]
        self.model.appendRow([None, type, nomenclature, rent, id], parent)
        self.proxy.invalidate()

    def confirm_detail_adding(self, data: List[Any]):

        self.ui.detailsView.insertRow(self.ui.detailsView.rowCount())

        for column, data in enumerate(data):
            data = str(data) if data else '-'
            row = self.ui.detailsView.rowCount() - 1
            item = QTableWidgetItem(str(data))
            self.ui.detailsView.setItem(row, column, item)

    def confirm_product_removing(self):
        index = self.proxy.mapToSource(self.ui.productsView.currentIndex())
        id_index = self.model.index(index.row(), 0, QModelIndex())
        id = self.model.data(id_index, Qt.DisplayRole)

        success = StandardDataService.delete_by_id(
            'products',
            {'product_id': id}
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

    def confirm_article_removing(self):
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

    def confirm_detail_removing(self):
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
