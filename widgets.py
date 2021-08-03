import math
from typing import Dict, Any, Iterable, Optional, Tuple


from PyQt5.QtCore import (
    QPoint, QPointF, QRectF, QSizeF, Qt, pyqtSignal, QPropertyAnimation, QParallelAnimationGroup,
    QAbstractAnimation, QAbstractItemModel, QObject, QRect, QSize, QEvent,
    QLocale, QModelIndex
)
from PyQt5.QtWidgets import (
    QAbstractItemView, QApplication, QListView, QWidget, QToolButton, QVBoxLayout, QSizePolicy,
    QScrollArea, QStyleOptionViewItem, QComboBox, QPushButton,
    QStyledItemDelegate, QStyle, QGraphicsView
)
from PyQt5.QtGui import (
    QPixmap, QPainter, QPalette, QFont, QFontMetrics, QColor
)

import application_rc

from service import StandardDataService, Field
from models import IngotModel, OrderModel


class ZoomGraphicsView(QGraphicsView):
    """Представление для графической сцены с зумом на мышку"""

    def wheelEvent(self, event): # pylint: disable=invalid-name
        """Переопределение события поворота колеса мышки

        Поворот колеса мышки в пределах представления инициирует приближение с
        определённой интерсивностью в определённом месте представления

        :param event: Событие поворота колесом мышки
        :type event: QWheelEvent
        """
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setResizeAnchor(QGraphicsView.NoAnchor)

        old_pos = self.mapToScene(event.position().toPoint())

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        self.scale(zoom_factor, zoom_factor)

        new_pos = self.mapToScene(event.position().toPoint())

        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())


class ExclusiveButton(QPushButton):
    def __init__(self, name: str, index: int = None, parent: Optional[QObject] = None):
        super(ExclusiveButton, self).__init__(parent)
        self.index = index
        self.setText(name)
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
    def __init__(self, values: dict, parent: Optional[QObject] = None):
        super().__init__(parent)
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

    def displayText(self, value: Any, locale: QLocale) -> str:
        for name in self.values:
            if int(value) == self.values[name]:
                return name
        return 'Ошибка'
            

class OrderDelegate(QStyledItemDelegate):

    deleteIndexClicked = pyqtSignal(QModelIndex)
    editIndexClicked = pyqtSignal(QModelIndex)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super(OrderDelegate, self).__init__(parent)
        
        # Основные настройки
        self.__margin = 5
        self.__font_size = 12
        self.__reduction_factor = 0.8
        self.__icon_size = QSize(15, 15)

        # Неизменяемые настройки
        self.__default_status_color = QColor('#fff')
        self.__planned_status_color = QColor('#98ff98')
        self.__completed_status_color = QColor('#0ff')
        self.__info_columns = 2

        # Иконка удаления заказа
        self.__deleteIcon = QPixmap(':icons/remove.png').scaled(
            self.__icon_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        # Иконка редактирования заказа
        self.__editIcon = QPixmap(':icons/edit.png').scaled(
            self.__icon_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

    @property
    def margin(self) -> int:
        return self.__margin

    @margin.setter
    def margin(self, value: int) -> None:
        self.__margin = value

    @property
    def fontPointSize(self) -> int:
        return self.__font_size

    @fontPointSize.setter
    def fontPointSize(self, value: int) -> None:
        self.__font_size = value

    @property
    def reductionFactor(self) -> float:
        return self.__reduction_factor
    
    @reductionFactor.setter
    def reductionFactor(self, value: float) -> None:
        self.__reduction_factor = value

    @property
    def iconSize(self) -> QSize:
        return self.__icon_size

    @property
    def iconSize(self, w: int, h: int) -> None:
        self.__icon_size = QSize(w, h)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem,
              index: QModelIndex) -> None:
        _option = QStyleOptionViewItem(option)
        self.initStyleOption(_option, index)
        order: Dict[Any] = index.data(Qt.DisplayRole)

        # Границы работы отрисовщика и границы области с отступом от края
        origin_rect = QRect(_option.rect)
        content_rect = self._contentRectAdjusted(_option)
        bottom_edge = origin_rect.bottom()

        # Флаг проверки последней записи - у неё граница идёт от края до края
        is_last = (index.model().rowCount() - 1) == index.row()

        # Палитра рисования и шрифты
        palette = _option.palette
        title_font = QFont(_option.font)
        title_font.setPointSize(self.__font_size)
        small_font = QFont(_option.font)
        small_font.setPointSize(self._informationFontPointSize(title_font))
        
        # Начало отрисовки
        painter.save()
        painter.setClipping(True)
        painter.setClipRect(origin_rect)

        color = self._statusStateColor(_option, order)
        painter.fillRect(origin_rect, color)

        painter.setPen(palette.dark().color())
        # Линия под последним элементом рисуется от края до края
        # У остальных элементов нижняя граница рисуется с отступом от края
        painter.drawLine(
            origin_rect.left() if is_last else self.__margin, bottom_edge,
            origin_rect.right(), bottom_edge
        )  

        painter.setFont(title_font)
        painter.setPen(palette.text().color())
        title_text, title_rect = self._title(title_font, order)
        painter.drawText(
            title_rect.translated(content_rect.left(), content_rect.top()),
            self._textFlags(), title_text
        )

        painter.setFont(small_font)
        painter.setPen(palette.shadow().color())

        border = content_rect.top() + title_rect.height()
        half_margin = border + self.__margin // 2

        if _option.state & QStyle.StateFlag.State_MouseOver:
            painter.drawLine(
                content_rect.left(), half_margin,
                content_rect.left() + title_rect.width(), half_margin
            )

        for text, text_rect in self._info(border, small_font, order):
            painter.drawText(text_rect, self._textFlags(), text)

        if _option.state & QStyle.StateFlag.State_MouseOver:
            painter.drawPixmap(self._deleteIconPos(_option), self.__deleteIcon)
            if order['status_id'] != 3:
                painter.drawPixmap(self._editIconPos(_option), self.__editIcon)

        # Конец отрисовки
        painter.restore()

    def _contentRectAdjusted(self, option: QStyleOptionViewItem) -> QRectF:
        return QRect(option.rect).adjusted(self.__margin, self.__margin, 0, 0)

    def _statusStateColor(self, option: QStyleOptionViewItem,
                         order: Dict) -> QColor:
        # Базовый цвет без статуса и состояния - белый
        _color = self.__default_status_color
        
        # Классификация по статусу заказа - запланирован или завершён
        if order['status_id'] == 2:
            _color = self.__planned_status_color
        elif order['status_id'] == 3:
            _color = self.__completed_status_color
        
        # Классификация по состоянию элемента - выбран или под курсором
        if option.state & QStyle.StateFlag.State_Selected:
            _color = _color.darker(115)
        elif option.state & QStyle.StateFlag.State_MouseOver:
            _color = _color.darker(105)
        
        return _color

    def _title(self, font: QFont, order: Dict) -> Tuple[str, QRectF]:
        _text = f'Заказ №{order["id"]} ({order["name"]})'
        _text_box = self._textBox(font, _text)
        return _text, _text_box

    def _info(self, border: float, font: QFont, order: Dict) -> Iterable:
        _table = self._table_info(order)

        # Вычисление количества строк
        rows = math.ceil(len(_table) / self.__info_columns)
        width = 160
        height = 20

        for row, _text in enumerate(_table):
            _rect = QRect(self._textBox(font, _text))

            margin_left = width * int(row // rows) + self.__margin
            margin_top = height * int(row % rows) + border + self.__margin 

            yield _text, _rect.translated(margin_left, margin_top)

    def _table_info(self, order):
        efficiency_text = f'{round(order["efficiency"] * 100, 2)}%'
        if not order["efficiency"]:
            efficiency_text = 'Не указан'
        _, status_text = StandardDataService.get_by_id(
            'orders_statuses', Field('id', order['status_id']))
        articles_text = f'{order["articles"]} шт.'
        details_text = f'{order["details"]} шт.'
        return [
            f'Статус: {status_text}',
            f'Выход годного: {efficiency_text}',
            f'Изделий: {articles_text}',
            f'Заготовок: {details_text}',
        ]

    def _textBox(self, font: QFont, data: str) -> QRectF:
        dy = font.pointSize() + self.__margin
        return QFontMetrics(font).boundingRect(data).adjusted(0, dy, 0, dy)

    def _textFlags(self):
        return Qt.TextFlag.TextSingleLine | Qt.AlignmentFlag.AlignLeft

    def _informationFontPointSize(self, f: QFont) -> float:
        return int(self.__reduction_factor * f.pointSize())

    def sizeHint(self, option: QStyleOptionViewItem,
                 index: QModelIndex) -> QSize:
        _option = QStyleOptionViewItem(option)
        self.initStyleOption(_option, index)

        return QSize(_option.rect.width(), 90)

    def _deleteIconPos(self, option: QStyleOptionViewItem) -> QPointF:
        content_rect = self._contentRectAdjusted(option)
        return QPoint(
            content_rect.right() - self.__icon_size.width() - self.__margin,
            content_rect.top()
        )
    
    def _editIconPos(self, option: QStyleOptionViewItem) -> QPointF:
        content_rect = self._contentRectAdjusted(option)
        delete_pos = self._deleteIconPos(option)
        return QPoint(
            content_rect.right() - self.__icon_size.width() - self.__margin,
            delete_pos.y() + self.__icon_size.height() + self.__margin
        )

    def _deleteIconRect(self, option: QStyleOptionViewItem) -> QRectF:
        return self.__deleteIcon.rect().translated(self._deleteIconPos(option))

    def _editIconRect(self, option: QStyleOptionViewItem) -> QRectF:
        return self.__editIcon.rect().translated(self._editIconPos(option))

    def editorEvent(self, event: QEvent, model: QAbstractItemModel,
                    option: QStyleOptionViewItem, index: QModelIndex) -> bool:
        _option = QStyleOptionViewItem(option)
        self.initStyleOption(_option, index)

        if event.type() == QEvent.Type.MouseButtonRelease:
            if(self._deleteIconRect(_option).contains(event.pos())):
                self.deleteIndexClicked.emit(index)

            if(self._editIconRect(_option).contains(event.pos())):
                order = index.data(Qt.DisplayRole)
                if order['status_id'] != 3:
                    self.editIndexClicked.emit(index)

        return super().editorEvent(event, model, option, index)


class IngotSectionDelegate(QStyledItemDelegate):

    forgedIndexClicked = pyqtSignal(QModelIndex)
    deleteFromStorageClicked = pyqtSignal(QModelIndex)
    deleteFromOrderClicked = pyqtSignal(QModelIndex)
    margin = 5

    def __init__(self, show_close: bool = True, numerable: bool = False, parent: Optional[QObject] = None) -> None:
        super(IngotSectionDelegate, self).__init__(parent)
        self.show_close = show_close
        self.numerable = numerable

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        palette, rect, font = opt.palette, opt.rect, opt.font
        contentRect = QRect(rect.adjusted(self.margin * 2, self.margin, -self.margin * 2, -self.margin))
        font.setPointSize(8)

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
            painter.drawPixmap(self.closeIconPos(opt), self.closeIcon)

        painter.setPen(palette.shadow().color())
        painter.drawLine(rect.right(), rect.top(), rect.right(), rect.bottom())

        painter.setFont(font)
        painter.setPen(Qt.black)

        # Надпись с партией слитка        
        batch = f"{f'№{index.row()+1} ' if self.numerable else ''}Партия: {str(ingot['batch']) if ingot['status_id'] not in [3, 4] else 'нет'}"
        batch_rect = QRect(self._textBox(font, batch))
        batch_rect.moveTo(contentRect.left(), contentRect.top())
        painter.drawText(batch_rect, Qt.AlignCenter, batch)

        # Надпись с размерами слитка
        size = 'Размеры: ' + 'х'.join(map(str, ingot['size']))
        size_rect = QRect(self._textBox(font, size))
        size_rect.moveTo(contentRect.left(), contentRect.bottom() - size_rect.height() - self.margin)
        painter.drawText(size_rect, Qt.TextSingleLine, size)

        # Надпись со сплавом слитка
        fusion = 'Сплав: ' + StandardDataService.get_by_id('fusions', Field('id', ingot['fusion_id']))[1]
        fusion_rect = QRect(self._textBox(font, fusion))
        fusion_rect.moveTo(contentRect.left(), contentRect.bottom() - fusion_rect.height() - size_rect.height() - self.margin)
        painter.drawText(fusion_rect, Qt.TextSingleLine, fusion)

        # Иконка 
        if ingot['status_id'] != 2:
            self.forgeIcon = QPixmap(':icons/ingot.svg')
        else:
            self.forgeIcon = QPixmap(':icons/patch.png')
        self.forgeIcon = self.forgeIcon.scaled(110, 110, aspectRatioMode = Qt.AspectRatioMode.KeepAspectRatio, transformMode = Qt.TransformationMode.SmoothTransformation)
        painter.drawPixmap(self.forgeIconPos(opt), self.forgeIcon)

        painter.restore()

    def closeIconPos(self, opt: QStyleOptionViewItem):
        return QPoint(opt.rect.right() - self.closeIcon.width() - self.margin, opt.rect.top() + self.margin)

    def forgeIconPos(self, opt: QStyleOptionViewItem):
        return QPoint(opt.rect.left() + self.margin * 2.5, opt.rect.top() + self.margin * 5)

    def _textBox(self, font: QFont, data: str) -> QRect:
        return QFontMetrics(font).boundingRect(data).adjusted(0, 0, 1, 1)

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:

        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        # Минимальный размер 135х185, максимальный 135х"высота контейнера"
        return QSize(135, max(opt.rect.height(), 185))

    def editorEvent(self, event: QEvent, model: QAbstractItemModel, option: QStyleOptionViewItem, index: QModelIndex) -> bool:
        if event.type() == QEvent.Type.MouseButtonRelease:
            ingot = index.data(Qt.DisplayRole)
            if self.show_close:
                closeIconRect = self.closeIcon.rect().translated(self.closeIconPos(option))
                if closeIconRect.contains(event.pos()):
                    if ingot['order_id']:
                        self.deleteFromOrderClicked.emit(index)
                        return super().editorEvent(event, model, option, index)
                    else:
                        self.deleteFromStorageClicked.emit(index)
                        return super().editorEvent(event, model, option, index)
            forgeIconRect = self.forgeIcon.rect().translated(self.forgeIconPos(option))
            if ingot['status_id'] == 3 and forgeIconRect.contains(event.pos()):
                self.forgedIndexClicked.emit(index)
        return super().editorEvent(event, model, option, index)


class ResidualsSectionDelegate(QStyledItemDelegate):
    
    deleteIndexClicked = pyqtSignal(QModelIndex)
    margin = 5

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super(ResidualsSectionDelegate, self).__init__(parent)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        rect = QRect(opt.rect)
        palette = QPalette(opt.palette)
        title_font = QFont(opt.font)
        small_font = QFont(opt.font)
        contentRect = QRect(rect.adjusted(self.margin, self.margin, self.margin, self.margin))
        small_font.setPointSize(title_font.pointSize() * 0.87)

        bottomEdge = rect.bottom()
        lastIndex = (index.model().rowCount() - 1) == index.row()

        painter.save()
        painter.setClipping(True)
        painter.setClipRect(rect)

        residual = index.data(Qt.DisplayRole)

        fill_color = QColor(255, 255, 255)
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

        name_text = f'Остаток №{residual["num"]} ({residual["batch"]})'
        name_rect = QRect(self._textBox(title_font, name_text))
        name_rect.moveTo(contentRect.left(), contentRect.top())
        painter.drawText(name_rect, Qt.TextSingleLine | Qt.AlignBottom, name_text)

        painter.setFont(small_font)

        size_text = f'{residual["length"]} x {residual["width"]} x {residual["height"]}'
        size_rect = QRect(self._textBox(small_font, size_text))
        size_rect.moveTo(contentRect.left(), contentRect.top() + name_rect.height())
        painter.drawText(size_rect, Qt.TextSingleLine | Qt.AlignBottom, size_text)

        self.closeIcon = QPixmap(':icons/cancel.png').scaled(15, 15, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio, transformMode=Qt.TransformationMode.SmoothTransformation)
        self.closeIconPos = QPoint(contentRect.right() - 2 * self.closeIcon.width() + self.margin, contentRect.top())
        painter.drawPixmap(self.closeIconPos, self.closeIcon)

        painter.restore()

    def _textBox(self, font: QFont, data: str) -> QRect:
        return QFontMetrics(font).boundingRect(data).adjusted(0, 0, 10, 0)

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:

        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        return QSize(opt.rect.width(), 45)

    def editorEvent(self, event: QEvent, model: QAbstractItemModel, option: QStyleOptionViewItem, index: QModelIndex) -> bool:
        if event.type() == QEvent.MouseButtonRelease:
            closeIconRect = self.closeIcon.rect().translated(self.closeIconPos)
            if closeIconRect.contains(event.pos()):
                self.deleteIndexClicked.emit(index)
        return super().editorEvent(event, model, option, index)


if __name__ == '__main__':
    application = QApplication([])
    window = QListView()
    print(window.font().family())
    print(window.font().pointSize())
    # window.setFlow(QListView.LeftToRight)
    # window.setSelectionMode(QListView.MultiSelection)
    window.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

    # model = IngotModel('unused')
    model = OrderModel(Field('status_id', 1))
    model.setupModelData()

    # delegate = IngotSectionDelegate(window)
    delegate = OrderDelegate(window)

    window.setModel(model)
    window.setItemDelegate(delegate)
    window.show()

    application.exec()
