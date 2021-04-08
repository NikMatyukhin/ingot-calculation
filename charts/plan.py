import random
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtWidgets import (
    QGraphicsItem, QGraphicsScene, QStyleOptionGraphicsItem, QWidget,
    QGraphicsSceneHoverEvent, QMenu
)
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QFontMetrics, QTransform
)


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
        painter.setFont(self.font)

        if self.metr.horizontalAdvance(self.visible_text) > self.width:
            self.setToolTip(self.visible_text)
            return

        painter.drawText(self.x_pos, self.y_pos,
                         self.width, self.height,
                         Qt.AlignCenter,
                         self.visible_text)

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        self.draw_color = self.color.darker(190)
        self.update()

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent):
        self.draw_color = self.color
        self.update()


class CuttingPlanPainter:

    def __init__(self, scene: QGraphicsScene):
        self.scene = scene
        self.font = QFont('Segoe UI', 6)
        self.bin_lenght = 0
        self.bin_width = 0
        self.bin_depth = 0
        self.x_coords = set([0])
        self.y_coords = set([0])
        self.blanks = []
        self.blanks_colors = {}

    def setBin(self, length: float, width: float, depth: float):
        self.bin_lenght = length
        self.y_coords.add(length)
        self.bin_width = width
        self.x_coords.add(width)
        self.bin_depth = depth

    def addBlank(self, h: float, w: float, depth: float, x: float, y: float,
                 name: str):
        self.blanks.append([x, y, w, h, name])
        if name not in self.blanks_colors:
            self.blanks_colors[name] = self.randomColor()
        self.x_coords.add(x)
        self.x_coords.add(x + w)
        self.y_coords.add(y)
        self.y_coords.add(y + h)

    def drawPlan(self):
        self.drawBin()
        for blank in self.blanks:
            color = self.blanks_colors[blank[4]]
            item = DetailGraphicsItem(*blank, clr=color)
            item.setAcceptHoverEvents(True)
            self.scene.addItem(item)

    def drawBin(self):
        pen = QPen(QBrush(Qt.black, Qt.BrushStyle.SolidPattern), 1.0,
                   Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                   Qt.PenJoinStyle.RoundJoin)
        brush = QBrush(QColor(0, 0, 0), Qt.BrushStyle.DiagCrossPattern)
        self.scene.addRect(0.0, 0.0, self.bin_width, self.bin_lenght,
                           pen, brush)
        self.drawCoords()

    def drawCoords(self):
        self.scene.addLine(0, -10, self.bin_width, -10, QPen(QColor(0, 0, 0)))
        self.scene.addLine(-10, 0, -10, self.bin_lenght, QPen(QColor(0, 0, 0)))
        prev = None
        for x in sorted(list(self.x_coords)):
            x_t = self.scene.addText(str(x))
            x_t.setFont(self.font)
            w_t = x_t.boundingRect().width()
            x_t.setPos(x - w_t // 2, -30)
            if prev:
                h_p = prev.boundingRect().height()
                if x_t.collidesWithItem(prev):
                    x_t.setPos(x - w_t // 2, -30 - h_p // 2)
            prev = x_t
        for y in sorted(list(self.y_coords)):
            y_t = self.scene.addText(str(y))
            y_t.setFont(self.font)
            w_t = y_t.boundingRect().width()
            y_t.setPos(-w_t - 10, y - 12)
            if prev:
                w_p = prev.boundingRect().width()
                if y_t.collidesWithItem(prev):
                    y_t.setPos(-w_t - w_p - 10, y - 12)
            prev = y_t

    def randomColor(self):
        color = QColor()
        color.setNamedColor(
            "#"+''.join(
                [
                    random.choice('0123456789ABCDEF') for j in range(6)
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
        self.x_coords = set([0])
        self.y_coords = set([0])
