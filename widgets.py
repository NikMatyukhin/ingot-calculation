import application_rc
import typing
import math
from PySide6.QtCore import (
    QPoint, Qt, Signal, QPropertyAnimation, QParallelAnimationGroup, QModelIndex,
    QAbstractAnimation, QAbstractItemModel, QObject, QRect, QSize, QEvent
)
from PySide6.QtWidgets import (
    QApplication, QListView, QWidget, QToolButton, QVBoxLayout, QSizePolicy, QScrollArea, QLabel,
    QCheckBox, QFrame, QItemDelegate, QStyleOptionViewItem, QComboBox,
    QPushButton, QStyledItemDelegate, QStyle
)
from PySide6.QtGui import (
    QPixmap, QPainter, QPalette, QFont, QFontMetrics
)
from models import ListModel


class ExclusiveButton(QPushButton):

    def __init__(self, parent: typing.Optional[QObject] = None, depth: float = 0):
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


class ListValuesDelegate(QItemDelegate):

    def __init__(self, names_list, parent: typing.Optional[QObject] = None):
        super(ListValuesDelegate, self).__init__(parent)
        self.names = names_list

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem,
                     index: QModelIndex) -> QWidget:
        editor = QComboBox(parent)
        editor.addItems(self.names)
        return editor

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        value = index.model().data(index, Qt.EditRole)
        editor.setCurrentIndex(self.names.index(value))

    def setModelData(self, editor: QWidget, model: QAbstractItemModel,
                     index: QModelIndex):
        value = editor.currentText()
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor: QWidget,
                             option: QStyleOptionViewItem, index: QModelIndex):
        editor.setGeometry(option.rect)


class Plate(QWidget):

    checked = Signal(bool)

    def __init__(self, id: int, fusion: str, batch_number: int, sizes: list,
                 is_selected=True, is_leftover=False,
                 parent: typing.Optional[QObject] = None):
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


class Section(QWidget):

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


class OrderSectionDelegate(QStyledItemDelegate):

    deleteIndexClicked = Signal(QModelIndex)

    def __init__(self, parent: typing.Optional[QObject] = None) -> None:
        super(OrderSectionDelegate, self).__init__(parent)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem,
              index: QModelIndex) -> None:

        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        palette = QPalette(opt.palette)
        rect = QRect(opt.rect)
        title_font = QFont(opt.font)
        title_font.setPointSize(11)
        small_font = QFont(opt.font)
        small_font.setPointSize(self.informationFontPointSize(title_font))

        margin = 5
        contentRect = QRect(rect.adjusted(margin, margin, margin, margin))
        bottomEdge = rect.bottom()
        lastIndex = (index.model().rowCount() - 1) == index.row()
        self.deleteIcon = QPixmap(':icons/remove.png').scaled(15, 15, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.deleteIconPos = QPoint(contentRect.right() - self.deleteIcon.width() - margin * 2,
                               contentRect.top())

        painter.save()
        painter.setClipping(True)
        painter.setClipRect(rect)

        if opt.state & QStyle.State_Selected:
            painter.fillRect(rect, palette.midlight().color().darker(105))
        elif opt.state & QStyle.State_MouseOver:
            painter.fillRect(rect, palette.midlight().color())
        else:
            painter.fillRect(rect, palette.light().color())

        painter.setPen(palette.dark().color())

        if lastIndex:
            painter.drawLine(rect.left(), bottomEdge, rect.right(), bottomEdge)
        else:
            painter.drawLine(margin, bottomEdge, rect.right(), bottomEdge)    

        data_row = index.data(Qt.DisplayRole)

        storage = ' (на склад)' if data_row['is_on_storage'] else ''
        name_text = 'Заказ ' + data_row['order_name'] + storage
        name_rect = QRect(self.textBox(title_font, name_text))
        name_rect.moveTo(contentRect.left(), contentRect.top())

        painter.setFont(title_font)
        painter.setPen(palette.text().color())
        painter.drawText(name_rect, Qt.TextSingleLine, name_text)

        visible_info = {
            'status_name': 'Статус: ' + data_row['status_name'],
            'efficiency': 'Эффективность: ' + str(data_row['efficiency']) + '%',
            'article_number': 'Изделий: ' + str(data_row['article_number']) + ' шт',
            'detail_number': 'Заготовок: ' + str(data_row['detail_number']) + ' шт',
        }
        columns = 2
        rows = math.ceil(len(visible_info) / columns)

        painter.setFont(small_font)
        painter.setPen(palette.shadow().color())
        
        for row, key in enumerate(visible_info):
            row_text = visible_info[key]
            row_rect = QRect(self.textBox(small_font, row_text))
            
            margin_left = 160 * int((row + 1) > rows) + margin
            margin_top = 20 * int(row % rows) + name_rect.bottom() + margin 
            
            row_rect.moveTo(margin_left, margin_top)
            painter.drawText(row_rect, Qt.TextSingleLine, row_text)

        if opt.state & QStyle.State_Selected:
            painter.drawPixmap(self.deleteIconPos, self.deleteIcon)

        painter.restore()

    def textBox(self, font: QFont, data: str) -> QRect:
        return QFontMetrics(font).boundingRect(data).adjusted(0, 0, 1, 1)

    def informationFontPointSize(self, f: QFont) -> float:
        return 0.85 * f.pointSize()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:

        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        return QSize(opt.rect.width(), 70)
    
    def editorEvent(self, event: QEvent, model: QAbstractItemModel, option: QStyleOptionViewItem, index: QModelIndex) -> bool:
        if event.type() == QEvent.MouseButtonRelease:
            deleteIconRect = self.deleteIcon.rect().translated(self.deleteIconPos)

            if(deleteIconRect.contains(event.pos())):
                self.deleteIndexClicked.emit(index)
        return super().editorEvent(event, model, option, index)


def printData(index: QModelIndex):
    print(index.row(), index.data(Qt.DisplayRole)['order_name'])


if __name__ == '__main__':
    application = QApplication()
    window = QListView()

    model = ListModel(None)
    delegate = OrderSectionDelegate(window)
    delegate.deleteIndexClicked.connect(printData)
    window.setModel(model)
    window.setItemDelegate(delegate)
    window.show()

    application.exec_()