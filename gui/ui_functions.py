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

        self.ui.searchType.setStyleSheet('''
            QComboBox {
                background-color: white;
                border-radius: 3px;
                padding-left: 10px;
            }

            QComboBox QListView {
                background-color: white;
                border-top: 1px solid rgb(141, 141, 141);
                border-left: 2px solid rgb(255, 145, 67);
                border-right: 2px solid rgb(255, 145, 67);
                border-bottom: 2px solid rgb(255, 145, 67);
                selection-background-color: rgb(181, 181, 181);
            }

            QComboBox:hover {
                background-color: rgb(255, 145, 67);
            }

            QComboBox:on {
                background-color: white;
                border: 2px solid rgb(255, 145, 67);
                border-bottom: none;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
                padding-left: 8px;
                padding-bottom: 1px;
            }

            QComboBox::drop-down {
                subcontrol-origin: border;
                subcontrol-position: right;
                height: 20px;
                width: 30px;
                border-left: 1px solid rgb(141, 141, 141);
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }

            QComboBox::down-arrow {
                image: url(:icons/down-arrow.png);
            }''')

        self.ui.searchNumber.setStyleSheet('''
            QLineEdit {
                background-color: rgb(255, 255, 255);
                border: 0px solid;
                border-radius: 3px;
                padding-left: 10px;
            }

            QLineEdit:hover {
                border: 2px solid rgb(255, 145, 67);
                padding-left: 8px;
            }

            QLineEdit:focus {
                border: 2px solid rgb(255, 145, 67);
                padding-left: 8px;
            }''')

        self.ui.searchName.setStyleSheet('''
            QLineEdit {
                background-color: rgb(255, 255, 255);
                border: 0px solid;
                border-radius: 3px;
                padding-left: 10px;
            }

            QLineEdit:hover {
                border: 2px solid rgb(255, 145, 67);
                padding-left: 8px;
            }

            QLineEdit:focus {
                border: 2px solid rgb(255, 145, 67);
                padding-left: 8px;
            }''')

    def setTopbarShadow(self):
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setColor(QColor(0, 0, 0))
        self.shadow_effect.setYOffset(-5)
        self.shadow_effect.setXOffset(0)
        self.shadow_effect.setBlurRadius(20)
        self.ui.topBar.setGraphicsEffect(self.shadow_effect)
