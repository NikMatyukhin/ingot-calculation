from PySide6.QtCore import (Qt)
from PySide6.QtWidgets import (QApplication, QWidget)

from gui import ui_order_page


class OrderPage(QWidget):

    def __init__(self):
        super(OrderPage, self).__init__()
        self.ui = ui_order_page.Ui_Form()
        self.ui.setupUi(self)
