from PySide6.QtWidgets import (QGraphicsItem, QGraphicsScene,
                               QGraphicsView, QApplication,
                               QStyleOptionGraphicsItem, QWidget,
                               QGraphicsSceneHoverEvent, QMenu)
from PySide6.QtCore import (Qt, QRectF, QPointF)
from PySide6.QtGui import (QPainter, QPen, QBrush, QColor, QFont,
                           QFontMetrics, QTransform, QPixmap)
import application_rc


class PlateGraphicsItem(QGraphicsItem):

    def __init__(self, txt, x=0.0, y=0.0, clr=QColor(50, 50, 200),
                 parent=None):
        super(PlateGraphicsItem, self).__init__(parent)
        self.x_pos = x
        self.y_pos = y
        self.width = 120
        self.height = 60
        self.color = clr
        self.visible_text = txt
        self.parent_node = None
        self.child_nodes = []
        self.top_connecter = QPointF(self.x_pos + self.width // 2,
                                     self.y_pos)
        self.bottom_connecter = QPointF(self.x_pos + self.width // 2,
                                        self.y_pos + self.height)

        self.font = QFont('Century Gothic', 12)
        self.metr = QFontMetrics(self.font)

    def moveToPos(self, x, y):
        self.x_pos = x
        self.y_pos = y
        self.top_connecter = QPointF(self.x_pos + self.width // 2,
                                     self.y_pos)
        self.bottom_connecter = QPointF(self.x_pos + self.width // 2,
                                        self.y_pos + self.height)
        self.recalculation()

    def add_child(self, item_child):
        self.child_nodes.append(item_child)
        item_child.parent_node = self
        self.recalculation()

    def recalculation(self):
        margin = 30
        spacing = 120
        child_width = sum([child.width + spacing for child in self.child_nodes]) - spacing

        left_corner_x = self.bottom_connecter.x() - child_width // 2

        shift = 0
        for i, child in enumerate(self.child_nodes):
            child.moveToPos(left_corner_x + shift,
                            self.y_pos + self.height + margin)
            shift += child.width + spacing

    def boundingRect(self):
        pen_width = 1.0
        return QRectF(self.x_pos - pen_width / 2,
                      self.y_pos - pen_width / 2,
                      self.width + pen_width,
                      self.height + pen_width)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem,
              widget: QWidget):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(
            QPen(QBrush(Qt.black, Qt.BrushStyle.SolidPattern), 2.0,
                 Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                 Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(
            QBrush(self.color,
                   Qt.BrushStyle.SolidPattern))
        painter.drawRoundedRect(self.x_pos, self.y_pos,
                                self.width, self.height,
                                3.0, 3.0)
        painter.setFont(self.font)

        painter.drawText(self.x_pos, self.y_pos,
                         self.width, self.height,
                         Qt.AlignCenter,
                         self.visible_text)
        if self.parent_node:
            painter.drawLine(self.top_connecter,
                             self.parent_node.bottom_connecter)


class OperationGraphicsItem(QGraphicsItem):

    def __init__(self, x=0.0, y=0.0, node_type='cut', parent=None):
        super(OperationGraphicsItem, self).__init__(parent)
        self.x_pos = x
        self.y_pos = y
        self.radius = 30
        self.width = self.radius * 2
        self.height = self.radius * 2
        self.color = QColor(100, 100, 200)
        self.node_type = node_type
        self.parent_node = None
        self.child_nodes = []
        self.top_connecter = QPointF(self.x_pos + self.radius,
                                     self.y_pos)
        self.bottom_connecter = QPointF(self.x_pos + self.radius,
                                        self.y_pos + self.height)

    def moveToPos(self, x, y):
        self.x_pos = x
        self.y_pos = y
        self.top_connecter = QPointF(self.x_pos + self.radius,
                                     self.y_pos)
        self.bottom_connecter = QPointF(self.x_pos + self.radius,
                                        self.y_pos + self.height)
        self.recalculation()

    def add_child(self, item_child):
        self.child_nodes.append(item_child)
        item_child.parent_node = self
        self.recalculation()

    def recalculation(self):
        margin = 30
        spacing = 120
        child_width = sum([child.width + spacing for child in self.child_nodes]) - spacing

        left_corner_x = self.bottom_connecter.x() - child_width // 2

        shift = 0
        for i, child in enumerate(self.child_nodes):
            child.moveToPos(left_corner_x + shift,
                            self.y_pos + self.height + margin)
            shift += child.width + spacing

    def boundingRect(self):
        pen_width = 1.0
        return QRectF(self.x_pos - pen_width / 2,
                      self.y_pos - pen_width / 2,
                      self.radius * 2 + pen_width,
                      self.radius * 2 + pen_width)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem,
              widget: QWidget):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(
            QPen(QBrush(Qt.black, Qt.BrushStyle.SolidPattern), 2.0,
                 Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                 Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(
            QBrush(self.color,
                   Qt.BrushStyle.SolidPattern))
        painter.drawEllipse(self.x_pos, self.y_pos,
                            self.radius * 2, self.radius * 2)

        image = None
        if self.node_type == 'roll':
            image = QPixmap(':/icons/roll.png')
        if self.node_type == 'cut':
            image = QPixmap(':/icons/scissors.png')
        if self.node_type == 'plan':
            image = QPixmap(':/icons/blueprint.png')
        painter.drawPixmap(self.x_pos + 15, self.y_pos + 15,
                           self.radius, self.radius, image)

        if self.parent_node:
            painter.drawLine(self.top_connecter,
                             self.parent_node.bottom_connecter)


def draw_map(m_scene: QGraphicsScene, map):
    item_1 = PlateGraphicsItem('Слиток\n180x160x28', clr=QColor(200, 100, 100))

    item_2 = OperationGraphicsItem(node_type='roll')
    item_1.add_child(item_2)
    print(item_2.x_pos, item_2.y_pos, item_2.width, item_2.height, item_2.bottom_connecter)

    item_3 = PlateGraphicsItem('Лист\n180x1357x3.3', clr=QColor(255, 255, 255))
    print(item_3.x_pos, item_3.y_pos, item_3.width, item_3.height, item_3.top_connecter)
    item_2.add_child(item_3)
    print(item_3.x_pos, item_3.y_pos, item_3.width, item_3.height, item_3.top_connecter)

    item_4 = OperationGraphicsItem(node_type='cut')
    item_3.add_child(item_4)

    item_5 = PlateGraphicsItem('Смежный\nостаток\n180x1203x3.3', clr=QColor(100, 200, 100))
    item_6 = PlateGraphicsItem('Лист\n180x154x3.3', clr=QColor(255, 255, 255))
    item_4.add_child(item_5)
    item_4.add_child(item_6)
    
    item_7 = OperationGraphicsItem(node_type='cut')
    item_5.add_child(item_7)

    item_8 = OperationGraphicsItem(node_type='plan')
    item_6.add_child(item_8)

    item_9 = PlateGraphicsItem('Смежный\nостаток\n180x883x3.3', clr=QColor(100, 200, 100))
    item_10 = PlateGraphicsItem('Лист\n180x320x3.3', clr=QColor(255, 255, 255))
    item_7.add_child(item_9)
    item_7.add_child(item_10)

    item_11 = PlateGraphicsItem('2 заготовки\n100%', clr=QColor(100, 100, 200))
    item_8.add_child(item_11)

    item_12 = OperationGraphicsItem(node_type='cut')
    item_9.add_child(item_12)

    item_13 = OperationGraphicsItem(node_type='roll')
    item_10.add_child(item_13)

    item_14 = PlateGraphicsItem('Смежный\nостаток\n180x774x3.3', clr=QColor(100, 200, 100))
    item_15 = PlateGraphicsItem('Лист\n180x109x3.3', clr=QColor(255, 255, 255))
    item_12.add_child(item_14)
    item_12.add_child(item_15)

    item_16 = PlateGraphicsItem('Лист\n198x320x3', clr=QColor(255, 255, 255))
    item_13.add_child(item_16)

    item_17 = OperationGraphicsItem(node_type='plan')
    item_16.add_child(item_17)

    item_18 = PlateGraphicsItem('4 заготовки\n93.94%', clr=QColor(255, 255, 255))
    item_17.add_child(item_18)

    m_scene.addItem(item_1)
    m_scene.addItem(item_2)
    m_scene.addItem(item_3)
    m_scene.addItem(item_4)
    m_scene.addItem(item_5)
    m_scene.addItem(item_6)
    m_scene.addItem(item_7)
    m_scene.addItem(item_8)
    m_scene.addItem(item_9)
    m_scene.addItem(item_10)
    m_scene.addItem(item_11)
    m_scene.addItem(item_12)
    m_scene.addItem(item_13)
    m_scene.addItem(item_14)
    m_scene.addItem(item_15)
    m_scene.addItem(item_16)
    m_scene.addItem(item_17)
    m_scene.addItem(item_18)


if __name__ == '__main__':
    app = QApplication()
    view = QGraphicsView()
    view.setDragMode(QGraphicsView.ScrollHandDrag)
    scene = QGraphicsScene()

    draw_map(scene, map)

    view.setScene(scene)
    view.show()
    app.exec_()
