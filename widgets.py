from logging import currentframe
import math
import typing
import application_rc

from PyQt5.QtCore import (
    QPoint, Qt, pyqtSignal, QPropertyAnimation, QParallelAnimationGroup,
    QAbstractAnimation, QAbstractItemModel, QObject, QRect, QSize, QEvent,
    QLocale, QModelIndex
)
from PyQt5.QtWidgets import (
    QApplication, QListView, QWidget, QToolButton, QVBoxLayout, QSizePolicy,
    QScrollArea, QItemDelegate, QStyleOptionViewItem, QComboBox, QPushButton,
    QStyledItemDelegate, QStyle
)
from PyQt5.QtGui import (
    QBrush, QPen, QPixmap, QPainter, QPalette, QFont, QFontMetrics, QColor
)

from service import StandardDataService, Field
from models import IngotModel


class ExclusiveButton(QPushButton):
    def __init__(self, parent: typing.Optional[QObject] = None,
                 depth: float = 0, name='', index=0):
        super(ExclusiveButton, self).__init__(parent)
        self.depth = depth
        self.index = index
        if name:
            self.setText(name)
        else:
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


class ListValuesDelegate(QStyledItemDelegate):

    def __init__(self, values: dict, parent: typing.Optional[QObject] = None):
        super(ListValuesDelegate, self).__init__(parent)
        self.values = values

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QWidget:
        editor = QComboBox(parent)
        editor.addItems(list(self.values.keys()))
        return editor

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        value: int = index.model().data(index, Qt.DisplayRole)
        for name in self.values:
            if int(value) == self.values[name]:
                editor.setCurrentText(name)
                break

    def setModelData(self, editor: QWidget, model: QAbstractItemModel,index: QModelIndex):
        value: str = editor.currentText()
        model.setData(index, self.values[value], Qt.EditRole)

    def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        editor.setGeometry(option.rect)
    
    def displayText(self, value: typing.Any, locale: QLocale) -> str:
        for name in self.values:
            if int(value) == self.values[name]:
                return name


class Section(QWidget):

    clicked = pyqtSignal()

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

    deleteIndexClicked = pyqtSignal(QModelIndex)
    margin = 5   

    def __init__(self, parent: typing.Optional[QObject] = None) -> None:
        super(OrderSectionDelegate, self).__init__(parent)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        rect = QRect(opt.rect)
        palette = QPalette(opt.palette)
        title_font = QFont(opt.font)
        small_font = QFont(opt.font)
        contentRect = QRect(rect.adjusted(self.margin, self.margin, self.margin, self.margin))
        
        title_font.setPointSize(11)
        small_font.setPointSize(self.informationFontPointSize(title_font))
        
        bottomEdge = rect.bottom()
        lastIndex = (index.model().rowCount() - 1) == index.row()
        self.deleteIcon = QPixmap(':icons/remove.png').scaled(15, 15, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.deleteIconPos = QPoint(contentRect.right() - self.deleteIcon.width() - self.margin * 2, contentRect.top())

        painter.save()
        painter.setClipping(True)
        painter.setClipRect(rect)

        order = index.data(Qt.DisplayRole)

        fill_color = palette.light().color()
        if order['status_id'] == 3:
            fill_color = QColor('#77e07e')
        if opt.state & QStyle.State_Selected:
            painter.fillRect(rect, fill_color.darker(115))
        elif opt.state & QStyle.State_MouseOver:
            painter.fillRect(rect, fill_color.darker(105))
        else:
            painter.fillRect(rect, fill_color)

        painter.setPen(palette.dark().color())
        if lastIndex:
            painter.drawLine(rect.left(), bottomEdge, rect.right(), bottomEdge)
        else:
            painter.drawLine(self.margin, bottomEdge, rect.right(), bottomEdge)    

        painter.setFont(title_font)
        painter.setPen(palette.text().color())

        name_text = 'Заказ №' + str(order['id']) + ' (' + order['name'] + ')'
        name_rect = QRect(self.textBox(title_font, name_text))
        name_rect.moveTo(contentRect.left(), contentRect.top())

        painter.drawText(name_rect, Qt.TextSingleLine, name_text)

        efficiency_text = str(round(order['efficiency'] * 100, 2)) + '%' if order['efficiency'] > 0.0 else 'Не указан'
        status_text = StandardDataService.get_by_id('orders_statuses', Field('id', order['status_id']))[1]
              
        visible_info = {
            'status_name': f'Статус: {status_text}',
            'efficiency': f'Выход годного: {efficiency_text}',
            'article_number': f'Изделий: {order["articles"]} шт',
            'detail_number': f'Заготовок: {order["details"]} шт',
        }
        columns = 2
        rows = math.ceil(len(visible_info) / columns)

        painter.setFont(small_font)
        painter.setPen(palette.shadow().color())
        
        for row, key in enumerate(visible_info):
            row_text = visible_info[key]
            row_rect = QRect(self.textBox(small_font, row_text))
            
            margin_left = 160 * int((row + 1) > rows) + self.margin
            margin_top = 20 * int(row % rows) + name_rect.bottom() + self.margin 
            
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


class IngotSectionDelegate(QStyledItemDelegate):

    forgedIndexClicked = pyqtSignal(QModelIndex)
    deleteFromStorageClicked = pyqtSignal(QModelIndex)
    deleteFromOrderClicked = pyqtSignal(QModelIndex)
    margin = 5

    def __init__(self, show_close: bool = True, numerable: bool = False, parent: typing.Optional[QObject] = None) -> None:
        super(IngotSectionDelegate, self).__init__(parent)
        self.show_close = show_close
        self.numerable = numerable
    
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        palette = QPalette(opt.palette)
        rect = QRect(opt.rect)
        contentRect = QRect(rect.adjusted(self.margin * 2, self.margin, -self.margin * 2, -self.margin))
        font = QFont(opt.font)

        font.setPointSize(8)
        # font.setBold(True)

        ingot = index.data(Qt.DisplayRole)
        fill_color = palette.light().color()
        if ingot['status_id'] in [3, 4]:
            fill_color = QColor('#77e07e') 

        painter.save()
        painter.setClipping(True)
        painter.setClipRect(rect)

        if opt.state & QStyle.State_Selected:
            painter.fillRect(rect, fill_color.darker(115))
            painter.fillRect(rect.adjusted(0, rect.height() - self.margin, 0, 0), QColor("#CD743D"))
        elif opt.state & QStyle.State_MouseOver:
            painter.fillRect(rect, fill_color.darker(105))
        else:
            painter.fillRect(rect, fill_color)
        
        if self.show_close:
            self.closeIcon = QPixmap(':icons/cancel.png').scaled(15, 15, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio, transformMode=Qt.TransformationMode.SmoothTransformation)
            self.closeIconPos = QPoint(contentRect.right() - self.closeIcon.width() + self.margin, contentRect.top())
            painter.drawPixmap(self.closeIconPos, self.closeIcon)
        
        painter.setPen(palette.shadow().color())
        painter.drawLine(rect.right(), rect.top(), rect.right(), rect.bottom())
        
        painter.setFont(font)
        painter.setPen(Qt.black)

        # Надпись с партией слитка        
        batch = f"{f'№{index.row()+1} ' if self.numerable else ''}Партия: {str(ingot['batch']) if ingot['status_id'] not in [3, 4] else 'нет'}"
        batch_rect = QRect(self.textBox(font, batch))
        batch_rect.moveTo(contentRect.left(), contentRect.top())
        painter.drawText(batch_rect, Qt.AlignCenter, batch)

        # Надпись с размерами слитка
        size = 'Размеры: ' + 'х'.join(map(str, ingot['size']))
        size_rect = QRect(self.textBox(font, size))
        size_rect.moveTo(contentRect.left(), contentRect.bottom() - size_rect.height() - self.margin)
        painter.drawText(size_rect, Qt.TextSingleLine, size)

        # Надпись со сплавом слитка
        fusion = 'Сплав: ' + StandardDataService.get_by_id('fusions', Field('id', ingot['fusion_id']))[1]
        fusion_rect = QRect(self.textBox(font, fusion))
        fusion_rect.moveTo(contentRect.left(), contentRect.bottom() - fusion_rect.height() - size_rect.height() - self.margin)
        painter.drawText(fusion_rect, Qt.TextSingleLine, fusion)

        # Иконка 
        free_height = fusion_rect.top() - batch_rect.bottom() - self.margin * 2
        free_height = min(contentRect.width(), free_height)
        if ingot['status_id'] != 2:
            self.forgeIcon = QPixmap(':icons/ingot.svg')
        else:
            self.forgeIcon = QPixmap(':icons/patch.png')
        self.forgeIcon = self.forgeIcon.scaled(free_height, free_height, aspectRatioMode = Qt.AspectRatioMode.KeepAspectRatio, transformMode = Qt.TransformationMode.SmoothTransformation)
        icon_left_margin = contentRect.width() // 2 - free_height // 2
        self.forgeIconPos = QPoint(contentRect.left() + icon_left_margin, contentRect.top() + self.margin + batch_rect.height())
        painter.drawPixmap(self.forgeIconPos, self.forgeIcon)

        painter.restore()
    
    def textBox(self, font: QFont, data: str) -> QRect:
        return QFontMetrics(font).boundingRect(data).adjusted(0, 0, 1, 1)
    
    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:

        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        return QSize(135, opt.rect.height())

    def editorEvent(self, event: QEvent, model: QAbstractItemModel, option: QStyleOptionViewItem, index: QModelIndex) -> bool:
        if event.type() == QEvent.MouseButtonRelease:
            ingot = index.data(Qt.DisplayRole)
            if self.show_close:
                closeIconRect = self.closeIcon.rect().translated(self.closeIconPos)
                if closeIconRect.contains(event.pos()):
                    if ingot['order_id']:
                        self.deleteFromOrderClicked.emit(index)
                    else:
                        self.deleteFromStorageClicked.emit(index)
            forgeIconRect = self.forgeIcon.rect().translated(self.forgeIconPos)
            if ingot['status_id'] == 3 and forgeIconRect.contains(event.pos()):
                self.forgedIndexClicked.emit(index)
        return super().editorEvent(event, model, option, index)


if __name__ == '__main__':
    application = QApplication()
    window = QListView()
    window.setFlow(QListView.LeftToRight)
    window.setSelectionMode(QListView.MultiSelection)

    model = IngotModel()
    model.setupModelData()

    delegate = IngotSectionDelegate(window)

    window.setModel(model)
    window.setItemDelegate(delegate)
    window.show()

    application.exec_()