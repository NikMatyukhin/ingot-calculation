import math
from typing import Dict, Any, Iterable, List, Optional, Tuple


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
    """Заранее преднастроенная кнопка для толщин"""
    
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
    """Класс для отображения словарных данных"""

    def __init__(self, values: dict, parent: Optional[QObject] = None):
        super(ListValuesDelegate, self).__init__(parent)
        
        # Словарь с отображаемыми данными
        self.values = values

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem,
                     index: QModelIndex) -> QWidget:
        editor = QComboBox(parent)
        # Ключами являются словесные именования каждого значения
        editor.addItems(list(self.values.keys()))
        return editor

    def setEditorData(self, editor: QComboBox, index: QModelIndex):
        # Данные модели при этом являются ID из базы данных
        value: int = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        for name in self.values:
            if int(value) == self.values[name]:
                editor.setCurrentText(name)
                break

    def setModelData(self, editor: QComboBox, model: QAbstractItemModel,
                     index: QModelIndex) -> None:
        value: str = editor.currentText()
        model.setData(index, self.values[value], Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor: QComboBox,
                             option: QStyleOptionViewItem,
                             index: QModelIndex) -> None:
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
            _rect = self._textBox(font, _text)

            margin_left = width * int(row // rows) + self.__margin
            margin_top = height * int(row % rows) + border + self.__margin 

            yield _text, _rect.translated(margin_left, margin_top)

    def _table_info(self, order: Dict) -> List[str]:
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
        return QFontMetrics(font).boundingRect(data).adjusted(0, dy, dy, dy)

    def _textFlags(self) -> int:
        return Qt.TextFlag.TextSingleLine | Qt.AlignmentFlag.AlignLeft

    def _informationFontPointSize(self, font: QFont) -> float:
        return int(self.__reduction_factor * font.pointSize())

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
            if self._deleteIconRect(_option).contains(event.pos()):
                self.deleteIndexClicked.emit(index)

            if self._editIconRect(_option).contains(event.pos()):
                order = index.data(Qt.DisplayRole)
                if order['status_id'] != 3:
                    self.editIndexClicked.emit(index)

        return super().editorEvent(event, model, option, index)


class IngotSectionDelegate(QStyledItemDelegate):

    orderedIndexClicked = pyqtSignal(QModelIndex)
    deliveredIndexClicked = pyqtSignal(QModelIndex)
    deleteFromStorageClicked = pyqtSignal(QModelIndex)
    deleteFromOrderClicked = pyqtSignal(QModelIndex)

    def __init__(self, show_close: bool = True, numerable: bool = True,
                 parent: Optional[QObject] = None) -> None:
        super(IngotSectionDelegate, self).__init__(parent)
        
        # Основные настройки
        self.__margin = 5
        self.__font_size = 9
        self.__small_font_size = self.__font_size * 0.8
        self.__mark_size = QSize(110, 110)
        self.__icon_size = QSize(15, 15)

        # Неизменяемые настройки
        self.__show_close = show_close
        self.__numerable = numerable
        self.__default_status_color = QColor('#fff')
        self.__planned_status_color = QColor('#98ff98')
        self.__ordered_status_color = QColor('#ffff9f')
        self.__selected_state_color = QColor("#CD743D")

        # Этикетка металла типа "слиток"
        self.__ingotMark = QPixmap(':icons/ingot.svg').scaled(
            self.__mark_size,
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )

        # Этикетка металла типа "остаток"
        self.__residualMark = QPixmap(':icons/patch.png').scaled(
            self.__mark_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # Иконка удаления слитка
        self.__deleteIcon = QPixmap(':icons/cancel.png').scaled(
            self.__icon_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # Иконка доставки и заказа слитка
        self.__orderIcon = QPixmap(':icons/forged.png').scaled(
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
        self.__small_font_size = self.__font_size * 0.8

    @property
    def iconSize(self) -> QSize:
        return self.__icon_size

    @property
    def iconSize(self, w: int, h: int) -> None:
        self.__icon_size = QSize(w, h)

    @property
    def markSize(self) -> QSize:
        return self.__mark_size

    @property
    def markSize(self, w: int, h: int) -> None:
        self.__mark_size = QSize(w, h)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem,
                    index: QModelIndex) -> None:
        _option = QStyleOptionViewItem(option)
        self.initStyleOption(_option, index)
        ingot: Dict[Any] = index.data(Qt.DisplayRole)

        # Границы работы отрисовщика и границы области с отступом от края
        origin_rect = QRect(_option.rect)
        content_rect = self._contentRectAdjusted(_option)
        backlight_rect = self._backlightRect(_option)

        # Палитра рисования и шрифты
        palette = _option.palette
        font = QFont(_option.font)
        font.setPointSize(self.__small_font_size)
        font.setBold(True)
        
        # Начало отрисовки
        painter.save()
        painter.setClipping(True)
        painter.setClipRect(origin_rect)

        color = self._statusStateColor(_option, ingot)
        painter.fillRect(origin_rect, color)
        if _option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(backlight_rect, self.__selected_state_color)
        
        # Правая разделительная линия между слитками
        painter.setPen(palette.shadow().color())
        painter.drawLine(
            origin_rect.right(), origin_rect.top(),
            origin_rect.right(), origin_rect.bottom()
        )

        painter.setFont(font)
        painter.setPen(palette.text().color())

        # Надпись с партией слитка и его номером
        title_text, title_rect = self._title(font, ingot, _option)
        painter.drawText(
            title_rect.translated(content_rect.left(), content_rect.top()),
            self._textFlags(), title_text
        )

        # Смена типа шрифта для основных надписей
        font.setBold(False)
        font.setPointSize(self.__font_size)
        painter.setFont(font)

        # Надпись со сплавом слитка
        fusion_text, fusion_rect = self._fusion(font, ingot, _option)
        painter.drawText(
            fusion_rect.translated(
                content_rect.left(),
                content_rect.top() + title_rect.height() + self.__margin
            ), self._textFlags(), fusion_text
        )

        # Надпись с размерами слитка
        size_text, size_rect = self._sizes(font, ingot, _option)
        painter.drawText(
            size_rect.translated(
                content_rect.left(),
                content_rect.bottom() - size_rect.height() - 2 * self.__margin
            ), self._textFlags(), size_text
        )

        # Этикетка металла
        top_edge = content_rect.top() + title_rect.height() + \
            fusion_rect.height() + self.__margin
        mark_pos = self._markPos(top_edge, _option)
        if ingot['status_id'] == 2:
            painter.drawPixmap(mark_pos, self.__residualMark)
        else:
            painter.drawPixmap(mark_pos, self.__ingotMark)
        
        # Иконка заказа слитка
        if ingot['status_id'] in [3, 5]:
            painter.drawPixmap(self._orderIconPos(_option), self.__orderIcon)
        
        # Иконка удаления слитка
        if self.__show_close:
            painter.drawPixmap(self._deleteIconPos(_option), self.__deleteIcon)
        
        painter.restore()

    def _contentRectAdjusted(self, option: QStyleOptionViewItem) -> QRectF:
        return QRectF(option.rect).adjusted(
            self.__margin * 2, self.__margin,
            -self.__margin * 2, -self.__margin
        )

    def _backlightRect(self, option: QStyleOptionViewItem) -> QRectF:
        _rect = QRectF(option.rect)
        return _rect.adjusted(0, _rect.height() - self.__margin, 0, 0)

    def _statusStateColor(self, option: QStyleOptionViewItem,
                         ingot: Dict) -> QColor:
        # Базовый цвет без статуса и состояния - белый
        _color = self.__default_status_color
        
        # Классификация по статусу заказа - запланирован или завершён
        if ingot['status_id'] in [3, 4]:
            _color = self.__planned_status_color
        elif ingot['status_id'] == 5:
            _color = self.__ordered_status_color
        
        # Классификация по состоянию элемента - выбран или под курсором
        if option.state & QStyle.StateFlag.State_Selected:
            _color = _color.darker(115)
        elif option.state & QStyle.StateFlag.State_MouseOver:
            _color = _color.darker(105)
        
        return _color

    def _title(self, font: QFont, ingot: Dict,
               option: QStyleOptionViewItem) -> Tuple[str, QRectF]:
        _text = ''
        if ingot['status_id'] in [1, 2]:
            _text = f'№{ingot["number"]} '
        elif ingot['status_id'] == 4:
            _text = f''
        else:
            _text = f'№{ingot["id"]} '
        if ingot['status_id'] in [1, 2]:
            _text += f'({str(ingot["batch"])})'
        else:
            _text += 'Нет партии'
        _text_rect = self._textBox(font, _text)
        _content_rect = self._contentRectAdjusted(option)
        if (dx := _content_rect.width() - _text_rect.width()) > 0:
            _text_rect.adjust(0, 0, dx, 0)
        return _text, _text_rect

    def _sizes(self, font: QFont, ingot: Dict,
               option: QStyleOptionViewItem) -> Tuple[str, QRectF]:
        _text = 'х'.join(map(str, ingot['size']))
        _text_rect = self._textBox(font, _text)
        _content_rect = self._contentRectAdjusted(option)
        if (dx := _content_rect.width() - _text_rect.width()) > 0:
            _text_rect.adjust(0, 0, dx, 0)
        return _text, _text_rect

    def _fusion(self, font: QFont, ingot: Dict,
                option: QStyleOptionViewItem) -> Tuple[str, QRectF]:
        _, _text, _ = StandardDataService.get_by_id(
            'fusions', Field('id', ingot['fusion_id'])
        )
        _text_rect = self._textBox(font, _text)
        _content_rect = self._contentRectAdjusted(option)
        if (dx := _content_rect.width() - _text_rect.width()) > 0:
            _text_rect.adjust(0, 0, dx, 0)
        return _text, _text_rect

    def _textFlags(self) -> int:
        return Qt.TextFlag.TextSingleLine | Qt.AlignmentFlag.AlignCenter

    def _deleteIconPos(self, option: QStyleOptionViewItem) -> QPointF:
        content_rect = self._contentRectAdjusted(option)
        return QPoint(
            content_rect.right() - self.__icon_size.width() + self.__margin,
            content_rect.top()
        )

    def _orderIconPos(self, option: QStyleOptionViewItem) -> QPointF:
        content_rect = self._contentRectAdjusted(option)
        top_pos = content_rect.top()
        if self.__show_close:
            top_pos = self._deleteIconPos(option).y() + \
                self.__icon_size.height() + self.__margin
        return QPoint(
            content_rect.right() - self.__icon_size.width() + self.__margin,
            top_pos
        )

    def _markPos(self, top: QPoint, option: QStyleOptionViewItem) -> QPointF:
        content_rect = self._contentRectAdjusted(option)
        return QPoint(content_rect.left(), top + 2 * self.__margin)

    def _textBox(self, font: QFont, data: str) -> QRectF:
        dy = font.pointSize() + self.__margin
        return QFontMetrics(font).boundingRect(data).adjusted(0, dy, 0, dy)

    def sizeHint(self, option: QStyleOptionViewItem,
                 index: QModelIndex) -> QSize:
        _option = QStyleOptionViewItem(option)
        self.initStyleOption(_option, index)

        # Минимальный размер 135х185, максимальный 135х"высота контейнера"
        return QSize(135, max(_option.rect.height(), 185))

    def _deleteIconRect(self, option: QStyleOptionViewItem) -> QRectF:
        return self.__deleteIcon.rect().translated(self._deleteIconPos(option))

    def _orderIconRect(self, option: QStyleOptionViewItem) -> QRectF:
        return self.__orderIcon.rect().translated(self._orderIconPos(option))

    def editorEvent(self, event: QEvent, model: QAbstractItemModel,
                    option: QStyleOptionViewItem, index: QModelIndex) -> bool:
        _option = QStyleOptionViewItem(option)
        self.initStyleOption(_option, index)
        ingot = index.data(Qt.ItemDataRole.DisplayRole)

        if event.type() == QEvent.Type.MouseButtonRelease:
            if self._deleteIconRect(_option).contains(event.pos()):
                if self.__show_close:
                    if ingot['order_id'] is None:
                        self.deleteFromStorageClicked.emit(index)
                    else:
                        self.deleteFromOrderClicked.emit(index)

            if self._orderIconRect(_option).contains(event.pos()):
                if ingot['status_id'] == 3:
                    self.orderedIndexClicked.emit(index)
                if ingot['status_id'] == 5:
                    self.deliveredIndexClicked.emit(index)

        return super().editorEvent(event, model, option, index)


class ResidualsSectionDelegate(QStyledItemDelegate):
    
    deleteIndexClicked = pyqtSignal(QModelIndex)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super(ResidualsSectionDelegate, self).__init__(parent)
        
        # Основные настройки
        self.__margin = 5
        self.__font_size = 9
        self.__reduction_factor = 0.8
        self.__icon_size = QSize(15, 15)

        # Неизменяемые настройки
        self.__default_status_color = QColor('#fff')
        
        # Иконка удаления слитка
        self.__deleteIcon = QPixmap(':icons/cancel.png').scaled(
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
        residual: Dict[Any] = index.data(Qt.ItemDataRole.DisplayRole)

        # Границы работы отрисовщика и границы области с отступом от края
        origin_rect = QRect(_option.rect)
        content_rect = self._contentRectAdjusted(_option)

        # Палитра рисования и шрифты
        palette = _option.palette
        title_font = QFont(_option.font)
        title_font.setPointSize(self.__font_size)
        small_font = QFont(_option.font)
        small_font.setPointSize(self._informationFontPointSize(title_font))

        bottom_edge = origin_rect.bottom()
        is_last = (index.model().rowCount() - 1) == index.row()

        painter.save()
        painter.setClipping(True)
        painter.setClipRect(origin_rect)

        color = self._statusStateColor(_option, residual)
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

        name_text, name_rect = self._name(title_font, residual)
        painter.drawText(
            name_rect.translated(
                content_rect.left(), content_rect.top()
            ), self._textFlags(), name_text
        )

        painter.setFont(small_font)

        size_text, size_rect = self._sizes(title_font, residual)
        painter.drawText(
            size_rect.translated(
                content_rect.left(), content_rect.top() + name_rect.height()
            ), self._textFlags(), size_text
        )
        
        painter.drawPixmap(self._deleteIconPos(_option), self.__deleteIcon)

        painter.restore()

    def _contentRectAdjusted(self, option: QStyleOptionViewItem) -> QRectF:
        return QRectF(option.rect).adjusted(
            self.__margin, self.__margin,
            -self.__margin, -self.__margin
        )

    def _statusStateColor(self, option: QStyleOptionViewItem,
                         ingot: Dict) -> QColor:
        # Базовый цвет без статуса и состояния - белый
        _color = self.__default_status_color
        
        # Классификация по состоянию элемента - выбран или под курсором
        if option.state & QStyle.StateFlag.State_Selected:
            _color = _color.darker(115)
        elif option.state & QStyle.StateFlag.State_MouseOver:
            _color = _color.darker(105)
        
        return _color

    def _informationFontPointSize(self, font: QFont) -> float:
        return int(self.__reduction_factor * font.pointSize())

    def _name(self, font: QFont, residual: Dict) -> Tuple[str, QRectF]:
        _text = str(f'№{residual["num"]} ({residual["batch"]}) - '
                    f'{residual["fusion"]}')
        _text_rect = self._textBox(font, _text)
        return _text, _text_rect

    def _sizes(self, font: QFont, residual: Dict) -> Tuple[str, QRectF]:
        _text = ' х '.join(map(
            str,
            [residual['length'], residual['width'], residual['height']]
        ))
        _text_rect = self._textBox(font, _text)
        return _text, _text_rect

    def _textBox(self, font: QFont, data: str) -> QRectF:
        dy = font.pointSize() + self.__margin
        return QFontMetrics(font).boundingRect(data).adjusted(0, dy, dy, dy)

    def _textFlags(self) -> int:
        return Qt.TextFlag.TextSingleLine | Qt.AlignmentFlag.AlignLeft

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:

        _option = QStyleOptionViewItem(option)
        self.initStyleOption(_option, index)

        return QSize(_option.rect.width(), 45)

    def _deleteIconPos(self, option: QStyleOptionViewItem) -> QPointF:
        content_rect = self._contentRectAdjusted(option)
        return QPoint(
            content_rect.right() - self.__icon_size.width() - self.__margin,
            content_rect.top()
        )

    def _deleteIconRect(self, option: QStyleOptionViewItem) -> QRectF:
        return self.__deleteIcon.rect().translated(self._deleteIconPos(option))

    def editorEvent(self, event: QEvent, model: QAbstractItemModel,
                    option: QStyleOptionViewItem, index: QModelIndex) -> bool:
        _option = QStyleOptionViewItem(option)
        self.initStyleOption(_option, index)
        
        if event.type() == QEvent.MouseButtonRelease:
            if self._deleteIconRect(_option).contains(event.pos()):
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
