import sys
from models import IngotModel
from typing import Optional, Union

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QWidget

from gui import ui_storage
from widgets import IngotSectionDelegate


class Storage(QDialog):

    def __init__(self, parent: Optional[QWidget] = None, flags: Union[Qt.WindowFlags, Qt.WindowType] = Qt.Window) -> None:
        super(Storage, self).__init__(parent, flags)
        self.ui = ui_storage.Ui_Dialog()
        self.ui.setupUi(self)

        self.used_ingots_model = IngotModel('used')
        self.unused_ingots_model = IngotModel('unused')
        self.planned_ingots_model = IngotModel('planned')

        self.ui.listView_2.setModel(self.used_ingots_model)
        self.ui.listView_3.setModel(self.unused_ingots_model)
        self.ui.listView.setModel(self.planned_ingots_model)

        self.ingot_delegate = IngotSectionDelegate(self)
        self.ui.listView.setItemDelegate(self.ingot_delegate)
        self.ui.listView_2.setItemDelegate(self.ingot_delegate)
        self.ui.listView_3.setItemDelegate(self.ingot_delegate)

    def confirm_ingot_adding(self):
        pass


if __name__ == '__main__':
    application = QApplication(sys.argv)
    window = Storage()
    window.show()
    sys.exit(application.exec())