from PySide6.QtWidgets import QPushButton


class ExclusiveButton (QPushButton):

    def __init__(self, parent=None, depth: float = 0):
        super(ExclusiveButton, self).__init__(parent)
        self.depth = depth
        self.setText(str(depth) + ' мм')
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setStyleSheet('''
            QPushButton {
                border: none;
                background-color: rgb(225, 225, 225);
                width: 80px;
                height: 40px;
                padding: 0px;
                color: black;
            }

            QPushButton:hover {
                background-color: rgb(235, 235, 235);
                border-bottom: 3px solid gray;
                font-weight: 800;
                padding-top: 3px;
            }

            QPushButton:pressed {
                background-color: rgb(245, 245, 245);
                border-bottom: 3px solid gray;
                font-weight: 800;
                padding-top: 3px;
            }

            QPushButton:checked {
                background-color: rgb(225, 225, 225);
                border-bottom: 3px solid black;
                padding-top: 3px;
                font-weight: 800;
            }''')
