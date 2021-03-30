from PySide6.QtWidgets import (QGraphicsItem, QGraphicsScene,
                               QGraphicsView, QApplication,
                               QStyleOptionGraphicsItem, QWidget,
                               QGraphicsSceneHoverEvent, QMenu)
from PySide6.QtCore import (Qt, QRectF, QPointF)
from PySide6.QtGui import (QPainter, QPen, QBrush, QColor, QFont,
                           QFontMetrics, QTransform)


plan = {
    "1.0": {
        "1": [
            {'x': 0.0, 'y': 0.0, 'w': 200.0, 'h': 200.0, 'idx': 1},
            {'x': 0.0, 'y': 200.0, 'w': 40.0, 'h': 40.0, 'idx': 2},
            {'x': 0.0, 'y': 240.0, 'w': 40.0, 'h': 40.0, 'idx': 3},
            {'x': 40.0, 'y': 200.0, 'w': 40.0, 'h': 40.0, 'idx': 4},
            {'x': 40.0, 'y': 240.0, 'w': 40.0, 'h': 40.0, 'idx': 5},
            {'x': 80.0, 'y': 200.0, 'w': 40.0, 'h': 40.0, 'idx': 6},
            {'x': 80.0, 'y': 240.0, 'w': 40.0, 'h': 40.0, 'idx': 7},
            {'x': 120.0, 'y': 200.0, 'w': 40.0, 'h': 40.0, 'idx': 8},
            {'x': 120.0, 'y': 240.0, 'w': 40.0, 'h': 40.0, 'idx': 9},
            {'x': 160.0, 'y': 200.0, 'w': 40.0, 'h': 40.0, 'idx': 10},
            {'x': 160.0, 'y': 240.0, 'w': 40.0, 'h': 40.0, 'idx': 11},
            {'x': 200.0, 'y': 0.0, 'w': 40.0, 'h': 40.0, 'idx': 12},
            {'x': 200.0, 'y': 40.0, 'w': 40.0, 'h': 40.0, 'idx': 13},
            {'x': 200.0, 'y': 80.0, 'w': 40.0, 'h': 40.0, 'idx': 14},
            {'x': 200.0, 'y': 120.0, 'w': 40.0, 'h': 40.0, 'idx': 15},
            {'x': 200.0, 'y': 160.0, 'w': 40.0, 'h': 40.0, 'idx': 16},
            {'x': 200.0, 'y': 200.0, 'w': 40.0, 'h': 40.0, 'idx': 17},
            {'x': 200.0, 'y': 240.0, 'w': 40.0, 'h': 40.0, 'idx': 18},
            {'x': 240.0, 'y': 0.0, 'w': 40.0, 'h': 40.0, 'idx': 19},
            {'x': 240.0, 'y': 40.0, 'w': 40.0, 'h': 40.0, 'idx': 20},
            {'x': 240.0, 'y': 80.0, 'w': 40.0, 'h': 40.0, 'idx': 21},
            {'x': 240.0, 'y': 120.0, 'w': 40.0, 'h': 40.0, 'idx': 22},
            {'x': 280.0, 'y': 0.0, 'w': 160.0, 'h': 100.0, 'idx': 23},
            {'x': 280.0, 'y': 100.0, 'w': 160.0, 'h': 200.0, 'idx': 24},
        ]
    }
}


class DetailGraphicsItem(QGraphicsItem):

    def __init__(self, x, y, w, h, idx, txt,
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


def draw_plan(m_scene: QGraphicsScene, plan):
    m_scene.addRect(0.0, 0.0, 500, 300,
                    QPen(QBrush(Qt.black, Qt.BrushStyle.SolidPattern), 2.0,
                         Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                         Qt.PenJoinStyle.RoundJoin),
                    QBrush(QColor(0, 0, 0),
                           Qt.BrushStyle.DiagCrossPattern))
    m_scene.addLine(0, -10, 500, -10, QPen(QColor(0, 0, 0)))
    m_scene.addLine(-10, 0, -10, 300, QPen(QColor(0, 0, 0)))
    x_coords = set()
    y_coords = set()
    for depth in plan:
        for priority in plan[depth]:
            for detail in plan[depth][priority]:
                x, y, w, h, idx = detail.values()
                x_coords.add(x)
                x_coords.add(x + w)
                y_coords.add(y)
                y_coords.add(y + h)
                item = DetailGraphicsItem(x, y, w, h, idx, f'Деталь №{idx}')
                item.setAcceptHoverEvents(True)
                m_scene.addItem(item)
    for x in x_coords:
        x_t = m_scene.addText(str(x))
        x_t.setPos(x - x_t.boundingRect().width() // 2, -30)
    for y in y_coords:
        y_t = m_scene.addText(str(y))
        y_t.setPos(-y_t.boundingRect().width() - 10, y - 12)


def detail_clicked(text: str, point: QPointF):
    global view
    item = view.itemAt(point)
    if item:
        print(f"Нажата деталь {item.index} "
              f"с размерами {item.width} на {item.height} "
              "была " + text)


def open_context_menu(point: QPointF):
    menu = QMenu()
    ready_action = menu.addAction('успешно вырезана')
    drop_action = menu.addAction('забракована')

    global view
    action = menu.exec_(view.mapToGlobal(point))
    detail_clicked(action.text(), point)


if __name__ == '__main__':
    app = QApplication()
    view = QGraphicsView()
    view.setContextMenuPolicy(Qt.CustomContextMenu)
    view.customContextMenuRequested.connect(open_context_menu)
    scene = QGraphicsScene()

    draw_plan(scene, plan)

    view.setScene(scene)
    view.show()
    app.exec_()
