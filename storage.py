import sys

from typing import Optional, Union

from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QWidget

from gui import ui_storage
from widgets import IngotSectionDelegate
from models import IngotModel
from service import Field, StandardDataService
from dialogs import IngotAddingDialog


class Storage(QDialog):
    def __init__(self, parent: Optional[QWidget] = None, flags: Union[Qt.WindowFlags, Qt.WindowType] = Qt.Window) -> None:
        super().__init__(parent, flags)
        self.ui = ui_storage.Ui_Dialog()
        self.ui.setupUi(self)

        self.used_ingots_model = IngotModel('used')
        self.unused_ingots_model = IngotModel('unused')
        self.planned_ingots_model = IngotModel('planned')
        self.ordered_ingots_model = IngotModel('ordered')

        self.ui.used_view.setModel(self.used_ingots_model)
        self.ui.unused_view.setModel(self.unused_ingots_model)
        self.ui.plan_view.setModel(self.planned_ingots_model)
        self.ui.ordered_view.setModel(self.ordered_ingots_model)

        self.ingot_delegate = IngotSectionDelegate(self)
        self.ingot_unclosable_delegate = IngotSectionDelegate(show_close=False, parent=self)
        self.ui.used_view.setItemDelegate(self.ingot_unclosable_delegate)
        self.ui.unused_view.setItemDelegate(self.ingot_delegate)
        self.ui.plan_view.setItemDelegate(self.ingot_unclosable_delegate)
        self.ui.ordered_view.setItemDelegate(self.ingot_unclosable_delegate)
        self.ui.unused_view.setFocus()

        self.ui.add.clicked.connect(self.open_ingot_dialog)
        self.ingot_delegate.deleteFromStorageClicked.connect(self.confirm_ingot_removing)

    def open_ingot_dialog(self):
        """Добавление нового слитка вручную"""
        window = IngotAddingDialog(self)
        window.ingotSavedSuccess.connect(self.confirm_ingot_adding)
        window.exec()

    def confirm_ingot_adding(self, ingot: dict):
        self.unused_ingots_model.appendRow(ingot)

    def confirm_ingot_removing(self, index: QModelIndex):
        ingot = self.unused_ingots_model.data(index, Qt.DisplayRole)

        message = QMessageBox(self)
        message.setWindowTitle('Подтверждение удаления')
        message.setText(f'Вы уверены, что хотите удалить слиток "{ingot["batch"]}"?')
        message.setIcon(QMessageBox.Icon.Question)
        answer = message.addButton('Да', QMessageBox.ButtonRole.AcceptRole)
        message.addButton('Отмена', QMessageBox.ButtonRole.RejectRole)
        message.exec()

        if answer == message.clickedButton():
            success = StandardDataService.delete_by_id('ingots', Field('id', ingot['id']))
            if not success:
                QMessageBox.critical(self, 'Ошибка удаления', 'Не удалось удалить слиток.', QMessageBox.Ok)
                return
            self.unused_ingots_model.deleteRow(index.row())
        self.ui.unused_view.setFocus()


if __name__ == '__main__':
    application = QApplication(sys.argv)
    storage_window = Storage()
    storage_window.show()
    sys.exit(application.exec())
