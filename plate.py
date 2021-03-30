import application_rc
from PySide6.QtCore import (Qt, Signal)
from PySide6.QtGui import (QIcon, QPixmap)
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QSizePolicy,
                               QLabel, QCheckBox, QFrame)


class Plate (QWidget):

    checked = Signal(bool)

    def __init__(self, id: int, fusion: str, batch_number: int, sizes: list,
                 is_selected=True, is_leftover=False, parent=None):
        super(Plate, self).__init__(parent)

        self.id = id
        self.batch_number = batch_number
        self.is_leftover = is_leftover
        self.is_selected = is_selected
        self.sizes = sizes

        self.main_frame = QFrame()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.main_frame)
        self.setLayout(main_layout)

        pixmap = None
        if fusion == 'ПлРд 90-10 ДС':
            pixmap = QPixmap(':icons/ingot-90-10-DC.png')
        elif fusion == 'ПлРд 90-10':
            pixmap = QPixmap(':icons/ingot-90-10.png')
        elif fusion == 'ПлРд 80-30':
            pixmap = QPixmap(':icons/ingot-80-30.png')
        elif fusion == 'ПлРд 80-20':
            pixmap = QPixmap(':icons/ingot-80-20.png')
        self.icon_label = QLabel()
        self.icon_label.setPixmap(pixmap)

        self.check_box = QCheckBox('Партия ' + str(self.batch_number))
        self.sizes_label = QLabel(f'{sizes[0]}x{sizes[1]}x{sizes[2]}')
        self.fusion_label = QLabel(fusion)

        if self.is_selected:
            self.check_box.setDisabled(True)
            self.check_box.setChecked(True)
        if self.is_leftover:
            self.check_box.hide()
        self.check_box.stateChanged.connect(self.check)

        self.setWidgetStyles()

        layout = QVBoxLayout()
        layout.addWidget(self.check_box)
        layout.addWidget(self.icon_label)
        layout.setAlignment(self.icon_label, Qt.AlignHCenter)
        layout.addWidget(self.sizes_label)
        layout.setAlignment(self.sizes_label, Qt.AlignHCenter)
        layout.addWidget(self.fusion_label)
        layout.setAlignment(self.fusion_label, Qt.AlignHCenter)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)
        layout.addStretch()
        self.main_frame.setLayout(layout)

    def setWidgetStyles(self):
        self.check_box.setStyleSheet('''
            QCheckBox {
                background-color: rgb(225, 225, 225);
            }''')

        self.main_frame.setStyleSheet('''
            QFrame {
                background-color: rgb(225, 225, 225);
                border-radius: 5px;
            }''')

    def getID(self):
        return self.id

    def check(self, check_state):
        self.checked.emit(check_state)
