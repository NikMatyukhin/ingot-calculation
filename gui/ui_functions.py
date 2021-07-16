from PyQt5.QtGui import (QIcon, QColor)
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QLabel,
                               QGraphicsDropShadowEffect)

from mainwindow import OCIMainWindow


class UIFunctions (OCIMainWindow):

    def setApplicationStyles(self):
        self.ui.searchResult_1.verticalScrollBar().setStyleSheet('''
            QScrollBar:vertical {
                border: none;
                background: rgb(240, 240, 240);
                width: 7px;
            }

            QScrollBar::handle:vertical {
                background-color: rgb(180, 180, 180);
                min-height: 30px;
                border-radius: 3px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: rgb(255, 145, 67);
            }

            QScrollBar::handle:vertical:pressed {
                background-color: rgb(223, 124, 59);
            }

            QScrollBar::sub-line:vertical {
                border: none;
                background-color: rgb(240, 240, 240);
                height: 7px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }

            QScrollBar::add-line:vertical {
                border: none;
                background-color: rgb(240, 240, 240);
                height: 7px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }

            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                background: none;
            }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }''')

        self.ui.searchResult_2.verticalScrollBar().setStyleSheet('''
            QScrollBar:vertical {
                border: none;
                background: rgb(240, 240, 240);
                width: 7px;
            }

            QScrollBar::handle:vertical {
                background-color: rgb(180, 180, 180);
                min-height: 30px;
                border-radius: 3px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: rgb(255, 145, 67);
            }

            QScrollBar::handle:vertical:pressed {
                background-color: rgb(223, 124, 59);
            }

            QScrollBar::sub-line:vertical {
                border: none;
                background-color: rgb(240, 240, 240);
                height: 7px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }

            QScrollBar::add-line:vertical {
                border: none;
                background-color: rgb(240, 240, 240);
                height: 7px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }

            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                background: none;
            }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }''')
