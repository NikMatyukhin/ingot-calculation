import random
from PyQt5.QtCore import QPoint, QRect, Qt, QRectF, QPointF
from PyQt5.QtWidgets import (
    QGraphicsItem, QGraphicsScene, QStyleOptionGraphicsItem, QWidget,
    QGraphicsSceneHoverEvent, QMenu, QGraphicsView
)
from PyQt5.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QFontMetrics, QPolygonF, QTransform,
    QPolygonF
)


class MyQGraphicsView(QGraphicsView):
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


class ButtEdgeGraphicsItem(QGraphicsItem):

    def __init__(self, x, y, w, h, parent=None):
        super(ButtEdgeGraphicsItem, self).__init__(parent)
        self.x_pos = x
        self.y_pos = y
        self.width = w
        self.height = h

    def boundingRect(self) -> QRectF:
        pen_width = 0.5
        return QRectF(self.x_pos - pen_width / 2,
                      self.y_pos - pen_width / 2,
                      self.width + pen_width,
                      self.height + pen_width)
    
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem,
              widget: QWidget) -> None:
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(QBrush(QColor(0, 0, 0, 80), Qt.BrushStyle.SolidPattern), 0.5,
                   Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                   Qt.PenJoinStyle.RoundJoin)
        brush = QBrush(QColor(0, 0, 0, 80), Qt.BrushStyle.DiagCrossPattern)
        
        rect = QRectF(self.x_pos, self.y_pos, self.width, self.height)
        
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawChord(rect, 15 * 16, 145 * 16)


class DetailGraphicsItem(QGraphicsItem):

    def __init__(self, x, y, w, h, txt, idx=0,
                 clr=QColor(100, 100, 100), parent=None):
        super(DetailGraphicsItem, self).__init__(parent)
        self.x_pos = x
        self.y_pos = y
        self.width = w
        self.height = h
        self.index = idx
        self.color = clr
        self.draw_color = clr
        self.visible_text = txt

        self.font = QFont('Century Gothic', 9)
        self.small_font = QFont('Century Gothic', 9)
        self.metr = QFontMetrics(self.font)

    def boundingRect(self):
        pen_width = 2.0
        return QRectF(self.x_pos - pen_width / 2,
                      self.y_pos - pen_width / 2,
                      self.width + pen_width,
                      self.height + pen_width)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem,
              widget: QWidget):
        painter.setPen(
            QPen(QBrush(Qt.black, Qt.BrushStyle.SolidPattern), 1.0,
                 Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                 Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(
            QBrush(self.draw_color,
                   Qt.BrushStyle.SolidPattern))
        painter.drawRect(self.x_pos, self.y_pos,
                         self.width, self.height)

        painter.setFont(self.small_font)
        painter.drawText(self.x_pos + 5, self.y_pos,
                         self.width, self.height - 5,
                         Qt.AlignLeft | Qt.AlignBottom,
                         f'{self.width}x{self.height}')
        if self.metr.horizontalAdvance(self.visible_text) > self.width:
            self.setToolTip(self.visible_text + f' {self.width}x{self.height}')
            return
        painter.setFont(self.font)
        painter.drawText(self.x_pos, self.y_pos,
                         self.width, self.height,
                         Qt.AlignCenter,
                         self.visible_text)

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        self.draw_color = self.color.darker(110)
        self.update()

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent):
        self.draw_color = self.color
        self.update()


class CuttingPlanPainter:

    def __init__(self, scene: QGraphicsScene):
        self.scene = scene
        self.font = QFont('Century Gothic', 6)
        self.bin_lenght = 0
        self.bin_width = 0
        self.bin_depth = 0
        # self.x_coords = set([0])
        # self.y_coords = set([0])
        self.vl_point = QPointF(1200, 1200)
        self.vr_point = QPointF(0, 0)
        self.lv_point = QPointF(1200, 1200)
        self.lb_point = QPointF(0, 0)
        self.blanks = []
        self.blanks_colors = {}

    def setBin(self, length: float, width: float, depth: float):
        self.bin_lenght = length
        self.bin_width = width
        self.bin_depth = depth

    def addBlank(self, h: float, w: float, depth: float, x: float, y: float,
                 name: str):
        self.blanks.append([x, y, w, h, name])
        if name not in self.blanks_colors:
            self.blanks_colors[name] = self.randomColor()
        if x < self.vl_point.x():
            self.vl_point.setX(x)
            self.vl_point.setY(y)
        if y < self.lv_point.y():
            self.lv_point.setX(x)
            self.lv_point.setY(y)
        if x+w > self.vr_point.x():
            self.vr_point.setX(x+w)
            self.vr_point.setY(y)
        if y+h > self.lb_point.y():
            self.lb_point.setX(x)
            self.lb_point.setY(y+h)
        # self.x_coords.add(x)
        # self.x_coords.add(x + w)
        # self.y_coords.add(y)
        # self.y_coords.add(y + h)

    def drawPlan(self):
        self.drawBin()
        for blank in self.blanks:
            color = self.blanks_colors[blank[4]]
            item = DetailGraphicsItem(*blank, clr=color)
            item.setAcceptHoverEvents(True)
            self.scene.addItem(item)
        self.drawCoords()

    def drawBin(self):
        pen = QPen(QBrush(QColor(0, 0, 0, 80), Qt.BrushStyle.SolidPattern), 0.5,
                   Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                   Qt.PenJoinStyle.RoundJoin)
        brush = QBrush(QColor(0, 0, 0, 80), Qt.BrushStyle.DiagCrossPattern)
        
        if self.blanks:
            bin_rect = QRectF(self.vl_point.x() - 2, self.vl_point.y() - 2, self.bin_width, self.bin_lenght)
            self.scene.addRect(bin_rect,pen, brush)
            text = self.scene.addText(f'Размер листа {self.bin_lenght}мм на {self.bin_width}мм')
            text.setPos(bin_rect.left(), bin_rect.bottom() + 5)

    def drawCoords(self):
        self.scene.addLine(self.vl_point.x(), -10,
                           self.vr_point.x(), -10,
                           QPen(QColor(0, 0, 0)))
        self.scene.addLine(-10, self.lv_point.y(),
                           -10, self.lb_point.y(),
                           QPen(QColor(0, 0, 0)))
        dashed_pen = QPen(QBrush(QColor(0, 0, 0), Qt.BrushStyle.SolidPattern), 0.5,
                          Qt.DashLine, Qt.RoundCap, Qt.RoundJoin)
        self.scene.addLine(self.vl_point.x(), -20,
                           self.vl_point.x(), self.vl_point.y(),
                           dashed_pen)
        self.scene.addLine(self.vr_point.x(), -20,
                           self.vr_point.x(), self.vr_point.y(),
                           dashed_pen)
        self.scene.addLine(-20, self.lv_point.y(),
                           self.lv_point.x(), self.lv_point.y(),
                           dashed_pen)
        self.scene.addLine(-20, self.lb_point.y(),
                           self.lb_point.x(), self.lb_point.y(),
                           dashed_pen)
        top_label = self.scene.addText(str(self.vr_point.x() - self.vl_point.x()))
        top_label.setPos((self.vl_point.x() + self.vr_point.x())/2, -30)
        bottom_label = self.scene.addText(str(self.lb_point.y() - self.lv_point.y()))
        bottom_label.setPos(-30, (self.lv_point.y() + self.lb_point.y())/2)
        bottom_label.setRotation(-90)

    def randomColor(self):
        color = QColor()
        color.setNamedColor(
            "#"+''.join(
                [
                    random.choice('456789ABCDEF') for j in range(6)
                ]
            )
        )
        return color

    def clearCanvas(self):
        self.scene.clear()
        self.bin_lenght = 0
        self.bin_width = 0
        self.bin_depth = 0
        self.blanks = []
        self.vl_point = QPointF(1200, 1200)
        self.vr_point = QPointF(0, 0)
        self.lv_point = QPointF(1200, 1200)
        self.lb_point = QPointF(0, 0)
        # self.x_coords = set([0])
        # self.y_coords = set([0])
