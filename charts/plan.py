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

        self.font = QFont('Century Gothic', 14)
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
            QPen(QBrush(Qt.black, Qt.BrushStyle.SolidPattern), 2.0,
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
        self.bin_lenght = 0
        self.bin_width = 0
        self.bin_depth = 0
        self.x_coords = set([0.0])
        self.y_coords = set([0.0])
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
        self.drawCoords()

    def drawBin(self):
        pen = QPen(QBrush(Qt.black, Qt.BrushStyle.SolidPattern), 2.0,
                   Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                   Qt.PenJoinStyle.RoundJoin)
        brush = QBrush(QColor(0, 0, 0), Qt.BrushStyle.DiagCrossPattern)
        self.scene.addRect(0.0, 0.0, self.bin_width, self.bin_lenght,
                           pen, brush)
        self.drawCoords()

    def drawCoords(self):
        self.scene.addLine(0, -10, self.bin_width, -10, QPen(QColor(0, 0, 0)))
        self.scene.addLine(-10, 0, -10, self.bin_lenght, QPen(QColor(0, 0, 0)))
        for x in self.x_coords:
            x_t = self.scene.addText(str(x))
            x_t.setPos(x - x_t.boundingRect().width() // 2, -30)
        for y in self.y_coords:
            y_t = self.scene.addText(str(y))
            y_t.setPos(-y_t.boundingRect().width() - 10, y - 12)

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
        self.x_coords = set([0.0])
        self.y_coords = set([0.0])
