import sys
import application_rc
from typing import Optional

from PyQt5.QtCore import Qt, QPointF, QModelIndex, QObject
from PyQt5.QtWidgets import (
    QApplication, QDialog, QMessageBox, QMenu, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QColor

import application_rc

from gui import ui_catalog
from service import CatalogDataService, Field, StandardDataService
from models import CatalogArticlesModel, CatalogDetailsModel, CatalogFilterProxyModel
from dialogs import ArticleDialog, DetailDialog
from widgets import ListValuesDelegate


ARTICLE_HEADERS = ['Ведомость',
                   'Название',
                   'Идентификатор',
                   ]
DETAIL_HEADERS = ['Название',
                  'Сплав',
                  'Длина',
                  'Ширина',
                  'Толщина',
                  'Количество',
                  'Приоритет',
                  'Направление проката',
                  'Идентификатор',
                  ]


class Catalog(QDialog):

    def __init__(self, parent: Optional[QObject] = None):
        super(Catalog, self).__init__(parent)
        self.ui = ui_catalog.Ui_Form()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.Window)

        self.directions_list = CatalogDataService.directions_list()
        self.fusions_list = CatalogDataService.fusions_list()

        self.articles_model = CatalogArticlesModel(ARTICLE_HEADERS)
        self.search_proxy = CatalogFilterProxyModel()
        self.search_proxy.setSourceModel(self.articles_model)
        self.details_model = CatalogDetailsModel(DETAIL_HEADERS)

        self.ui.articles_view.setModel(self.search_proxy)
        self.ui.articles_view.resizeColumnToContents(0)
        self.ui.articles_view.resizeColumnToContents(1)
        self.ui.articles_view.setColumnHidden(2, True)

        self.ui.details_view.setModel(self.details_model)
        self.direction_delegate = ListValuesDelegate(self.directions_list)
        self.fusion_delegate = ListValuesDelegate(self.fusions_list)
        self.ui.details_view.setItemDelegateForColumn(1, self.fusion_delegate)
        self.ui.details_view.setItemDelegateForColumn(7, self.direction_delegate)
        self.ui.details_view.hideColumn(8)

        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setColor(QColor(0, 0, 0))
        self.shadow_effect.setYOffset(-5)
        self.shadow_effect.setXOffset(0)
        self.shadow_effect.setBlurRadius(20)
        self.ui.top_frame.setGraphicsEffect(self.shadow_effect)

        self.ui.add_article.clicked.connect(self.open_article_dialog)
        self.ui.add_detail.clicked.connect(self.open_detail_dialog)
        self.ui.articles_view.clicked.connect(self.show_details)
        self.ui.name.textChanged.connect(self.search_proxy.name)
        self.articles_model.dataChanged.connect(self.update_article)
        self.details_model.dataChanged.connect(self.update_detail)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_details(self, current_index: QModelIndex):
        index = self.search_proxy.mapToSource(current_index)
        parent = self.articles_model.parent(index)
        
        if parent.isValid():
            return
        
        id_index = self.articles_model.index(index.row(), 0, parent)
        id = self.articles_model.data(id_index, Qt.DisplayRole)
        self.details_model.article = id

        for column in range(0, 8):
            self.ui.details_view.resizeColumnToContents(column)
        self.ui.details_view.setColumnWidth(1, 110)

    def show_context_menu(self, point: QPointF):
        """Метод вызова контекстного меню.

        Отвечает за добавление и удаление заготовок и изделий.

        :param point: Точка вызова контекстного меню
        :type point: QPointF
        """
        menu = QMenu()

        if self.ui.articles_view.hasFocus():
            if self.articles_model.rowCount(QModelIndex()):
                if not self.ui.articles_view.currentIndex().parent().isValid():
                    add = menu.addAction('Добавить заготовку')
                    delete = menu.addAction('Удалить изделие')
        
                    add.triggered.connect(self.open_detail_dialog)
                    delete.triggered.connect(self.confirm_article_removing)
        
        elif self.ui.details_view.hasFocus():
            add = menu.addAction('Добавить заготовку')
            delete = menu.addAction('Удалить заготовку')
        
            add.triggered.connect(self.open_detail_dialog)
            delete.triggered.connect(self.confirm_detail_removing)
        
        menu.exec_(self.mapToGlobal(point))

    def open_article_dialog(self):
        window = ArticleDialog(self)
        window.recordSavedSuccess.connect(self.confirm_article_adding)

        window.exec_()

    def open_detail_dialog(self):
        index = self.search_proxy.mapToSource(self.ui.articles_view.currentIndex())
        if not index.isValid():
            return False
        
        id_index = self.articles_model.index(index.row(), 0, QModelIndex())
        name_index = self.articles_model.index(index.row(), 1, QModelIndex())
        id = self.articles_model.data(id_index, Qt.DisplayRole)
        name = self.articles_model.data(name_index, Qt.DisplayRole)
        
        window = DetailDialog(name, id, self)
        window.recordSavedSuccess.connect(self.confirm_detail_adding)

        window.exec_()

    def update_article(self, index: QModelIndex, temp: QModelIndex, roles: list):
        id_index = self.articles_model.index(index.row(), 0, QModelIndex())
        name_index = self.articles_model.index(index.row(), 1, QModelIndex())

        id = self.articles_model.data(id_index, Qt.DisplayRole)
        name = self.articles_model.data(name_index, Qt.DisplayRole)

        success = StandardDataService.update_record('articles', Field('id', id), name=name)
        if not success:
            QMessageBox.critical(self, f'Ошибка обновления', f'SqlDatabaseError: can not update record.', QMessageBox.Ok)

    def update_detail(self, index: QModelIndex, temp: QModelIndex, roles: list):
        id_index = self.details_model.index(index.row(), 8, QModelIndex())
        id = self.details_model.data(id_index, Qt.DisplayRole)
        
        changed_index = self.details_model.index(index.row(), index.column(), QModelIndex())
        changed = self.details_model.data(changed_index, Qt.DisplayRole)

        if index.column() == 0:
            success = StandardDataService.update_record('details', Field('id', id), name=changed)
        elif index.column() == 1:
            success = StandardDataService.update_record('details', Field('id', id), fusion_id=changed)
        elif index.column() == 2:
            success = StandardDataService.update_record('details', Field('id', id), length=changed)
        elif index.column() == 3:
            success = StandardDataService.update_record('details', Field('id', id), width=changed)
        elif index.column() == 4:
            success = StandardDataService.update_record('details', Field('id', id), height=changed)
        elif index.column() == 5:
            success = StandardDataService.update_record('details', Field('id', id), amount=changed)
        elif index.column() == 6:
            success = StandardDataService.update_record('details', Field('id', id), priority=changed)
        elif index.column() == 7:
            success = StandardDataService.update_record('details', Field('id', id), direction_id=changed)
        
        if not success:
            QMessageBox.critical(self, f'Ошибка обновления', f'SqlDatabaseError: can not update record.', QMessageBox.Ok)

    def confirm_article_adding(self, data: list):
        self.articles_model.appendRow(data, QModelIndex())

    def confirm_detail_adding(self, data: list):
        self.details_model.appendRow(data, QModelIndex())

    def confirm_article_removing(self):
        index = self.search_proxy.mapToSource(self.ui.articles_view.currentIndex())
        id_index = self.articles_model.index(index.row(), 0, QModelIndex())
        id = self.articles_model.data(id_index, Qt.DisplayRole)
        
        success = StandardDataService.delete_by_id('articles', Field('id', id))
        if success:
            self.articles_model.removeRows(index.row(), 1, QModelIndex())
        else:
            QMessageBox.critical(self, 'Ошибка удаления', 'SqlDatabaseError: can not remove record.', QMessageBox.Ok)
        self.details_model.clear()

    def confirm_detail_removing(self):
        index = self.ui.details_view.currentIndex()
        id_index = self.details_model.index(index.row(), 8, QModelIndex())
        id = self.details_model.data(id_index, Qt.DisplayRole)

        success = StandardDataService.delete_by_id('details', Field('id', id))
        if success:
            self.details_model.removeRow(index.row(), QModelIndex())
        else:
            QMessageBox.critical(self, 'Ошибка удаления', 'SqlDatabaseError: can not remove record.', QMessageBox.Ok)


if __name__ == '__main__':
    application = QApplication(sys.argv)

    catalog_window = Catalog()
    catalog_window.show()

    sys.exit(application.exec())
