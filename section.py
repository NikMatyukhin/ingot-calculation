import application_rc
from PySide6.QtCore import (
    Qt, Signal, QPropertyAnimation, QParallelAnimationGroup, QAbstractAnimation
)
from PySide6.QtWidgets import (
    QWidget, QToolButton, QVBoxLayout, QSizePolicy, QScrollArea
)


class Section (QWidget):

    clicked = Signal()

    def __init__(self, id: int, name: str):
        super(Section, self).__init__()
        self.id = id
        self.name = name
        self.depth = None
        self.status = None
        self.efficiency = None

        self.toggle_button = QToolButton()
        self.toggle_button.setText(name)
        self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Maximum)

        self.content_area = QScrollArea()
        self.content_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.content_area.setMaximumHeight(0)
        self.content_area.setMinimumHeight(0)
        self.content_area.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.toggle_animation = QParallelAnimationGroup()
        self.toggle_animation.addAnimation(
            QPropertyAnimation(self, b"minimumHeight"))
        self.toggle_animation.addAnimation(
            QPropertyAnimation(self, b"maximumHeight"))
        self.toggle_animation.addAnimation(
            QPropertyAnimation(self.content_area, b"maximumHeight"))

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.toggle_button)
        self.main_layout.addWidget(self.content_area)
        self.setLayout(self.main_layout)

        self.setWidgetStyles()

        self.toggle_button.clicked.connect(self.toggle)

    def setWidgetStyles(self):
        self.toggle_button.setStyleSheet('''
            QToolButton {
                background-color: rgb(225, 225, 225);
                border: none;
                border-radius: 3px;
                height: 30px;
                padding-left: 10px;
            }

            QToolButton::down-arrow {
                image: url(:icons/down-arrow.png);
            }

            QToolButton::right-arrow {
                image: url(:icons/right-arrow.png);
            }

            QToolButton:hover {
                padding-left: 8px;
                background-color: rgb(200, 200, 200);
                border: 2px solid rgb(255, 145, 67);
            }

            QToolButton:checked {
                background-color: rgb(160, 160, 160);
                border: 2px solid rgb(255, 145, 67);
                border-bottom: none;
                padding-left: 8px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
            }''')

        self.content_area.setStyleSheet('''
            QScrollArea {
                border: 2px solid rgb(255, 145, 67);
                border-top: none;
                border-bottom-left-radius: 3px;
                border-bottom-right-radius: 3px;
            }

            QScrollArea QTableWidget {
                background-color: rgb(231, 231, 231);
            }''')

    def setContentFields(self, content_layout):
        self.content_area.setLayout(content_layout)
        collapsed_height = self.sizeHint().height() - \
            self.content_area.maximumHeight()
        content_height = content_layout.sizeHint().height() // 2 + 1
        for i in range(self.toggle_animation.animationCount() - 1):
            animation = self.toggle_animation.animationAt(i)
            animation.setDuration(150)
            animation.setStartValue(collapsed_height)
            animation.setEndValue(collapsed_height + content_height)
        animation = self.toggle_animation.animationAt(
            self.toggle_animation.animationCount() - 1)
        animation.setDuration(150)
        animation.setStartValue(0)
        animation.setEndValue(content_height)

    def toggle(self, check_state):
        if check_state:
            self.toggle_animation.setDirection(QAbstractAnimation.Forward)
            self.toggle_button.setArrowType(Qt.DownArrow)
        else:
            self.toggle_animation.setDirection(QAbstractAnimation.Backward)
            self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_animation.start()
        self.clicked.emit()

    def expand(self):
        self.toggle_animation.setDirection(QAbstractAnimation.Forward)
        self.toggle_button.setArrowType(Qt.DownArrow)
        self.toggle_button.setChecked(True)
        self.toggle_animation.start()

    def collapse(self):
        self.toggle_animation.setDirection(QAbstractAnimation.Backward)
        self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_button.setChecked(False)
        self.toggle_animation.start()
