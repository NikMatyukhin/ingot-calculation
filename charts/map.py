from PySide6.QtWidgets import (
    QGraphicsItem, QGraphicsScene, QGraphicsView, QApplication, QWidget,
    QStyleOptionGraphicsItem, QGraphicsSceneHoverEvent, QMenu
)
from PySide6.QtCore import Qt, QRectF, QPointF, QLineF, QSizeF
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QFontMetrics, QTransform, QPixmap,
    QPolygonF, QIcon
)
from sequential_mh.bpp_dsc.tree import (
    Operations, CuttingChartNode, is_op_node, is_bin_node, is_cc_node
)
from sequential_mh.bpp_dsc.rectangle import (
    BinType
)
from sequential_mh.bpp_dsc.support import dfs
import application_rc
from math import atan2, sin, cos


class PlateGraphicsItem (QGraphicsItem):

    def __init__(self, txt, x, y, clr=QColor(255, 255, 255)):
        super(PlateGraphicsItem, self).__init__()
        self.x_pos = x
        self.y_pos = y
        self.width = 120
        self.height = 60
        self.color = clr
        self.visible_text = txt
        self.left = QPointF(x, y + 30)
        self.right = QPointF(x + 120, y + 30)
        self.top = QPointF(x + 60, y)
        self.bottom = QPointF(x + 60, y + 60)

        self.font = QFont('Segoe UI', 9)
        self.metr = QFontMetrics(self.font)

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
        painter.setBrush(QBrush(self.color, Qt.BrushStyle.SolidPattern))
        painter.drawRoundedRect(self.x_pos, self.y_pos,
                                self.width, self.height,
                                3.0, 3.0)
        painter.setFont(self.font)
        painter.drawText(self.x_pos, self.y_pos,
                         self.width, self.height,
                         Qt.AlignCenter,
                         self.visible_text)


class OperationGraphicsItem (QGraphicsItem):

    def __init__(self, x, y, type):
        super(OperationGraphicsItem, self).__init__()
        self.x_pos = x
        self.y_pos = y
        self.radius = 30
        self.width = self.radius * 2
        self.height = self.radius * 2
        self.color = QColor(100, 100, 150)
        self.type = type

    @property
    def left(self):
        return QPointF(self.x_pos, self.y_pos + 30)

    @property
    def right(self):
        return QPointF(self.x_pos + 60, self.y_pos + 30)

    @property
    def top(self):
        return QPointF(self.x_pos + 30, self.y_pos)

    @property
    def bottom(self):
        return QPointF(self.x_pos + 30, self.y_pos + 60)

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
        if self.type == Operations.h_rolling:
            image = QPixmap(':/icons/h-roll.png')
        if self.type == Operations.v_rolling:
            image = QPixmap(':/icons/v-roll.png')
        if self.type == Operations.cutting:
            image = QPixmap(':/icons/scissors.png')
        if self.type == Operations.packing:
            image = QPixmap(':/icons/blueprint.png')
        icon = QIcon(image)
        icon.paint(painter, self.x_pos + 10, self.y_pos + 10,
                   self.radius + 10, self.radius + 10)


class Edge(QGraphicsItem):
    """Компонента отрисовки - ребро между двумя другими компонентами-блоками

    :param QGraphicsItem: Родительский класс всех компонент отрисовки
    :type QGraphicsItem: class
    """
    def __init__(self, source: QPointF, dest: QPointF):
        super(Edge, self).__init__()
        self.sourcePoint: QPointF = source
        self.destPoint: QPointF = dest
        self.arrowSize = 5

    def boundingRect(self):
        penWidth = 1
        extra = (penWidth + self.arrowSize) / 2.0

        return QRectF(
            self.sourcePoint,
            QSizeF(
                self.destPoint.x() - self.sourcePoint.x(),
                self.destPoint.y() - self.sourcePoint.y()
            )
        ).normalized().adjusted(-extra, -extra, extra, extra)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem,
              widget: QWidget):
        line = QLineF(self.sourcePoint, self.destPoint)
        painter.setPen(
            QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        )
        painter.drawLine(line)
        angle = atan2(-line.dy(), line.dx())

        M_PI = 3.14
        destArrowP1 = self.destPoint + QPointF(
            sin(angle - M_PI / 3) * self.arrowSize,
            cos(angle - M_PI / 3) * self.arrowSize
        )
        destArrowP2 = self.destPoint + QPointF(
            sin(angle - M_PI + M_PI / 3) * self.arrowSize,
            cos(angle - M_PI + M_PI / 3) * self.arrowSize
        )

        painter.setBrush(Qt.black)
        painter.drawPolygon(QPolygonF([line.p2(), destArrowP1, destArrowP2]))


class CuttingMapPainter:
    """Отрисовщик карты раскроя

    На полученной сцене после получения всех необходимых параметров составляет
    карту раскроя. Обход дерева раскроя осуществляется в глубину. Механика
    вывода слишком сложна и не поддаётся разумному описанию.
    """
    def __init__(self, scene: QGraphicsScene):
        self.scene = scene
        self.font = QFont('Segoe UI', 9)

    def setTree(self, tree):
        self.tree = tree

    def setEfficiency(self, efficiency):
        self.efficiency = efficiency

    def drawTree(self):
        self.cutting_nodes = []
        self.x = 0.0
        self.y = 0.0
        self.prev_item = None
        self.prev_type = None
        self.source_point = None
        self.in_width = True
        self.skip = False
        for node in dfs(self.tree):
            if is_op_node(node):
                if node.operation == Operations.rolling:
                    continue
            cur_item = self.createItem(node)
            self.scene.addItem(cur_item)
            if is_bin_node(node):
                print(node.bin.bin_type)
                if node.bin.bin_type == BinType.ingot:
                    efficiency = self.scene.addText(
                        'Выход годного:\n' + str(self.efficiency) + '%'
                    )
                    efficiency.setX(self.x - 140)
                    efficiency.setY(self.y - 60)
            if is_op_node(node):
                print(node.operation)
                if not self.in_width:
                    cur_item.x_pos += 30
            if self.prev_item and not self.skip:
                if self.in_width:
                    self.scene.addItem(Edge(self.source_point, cur_item.left))
                else:
                    self.scene.addItem(Edge(self.source_point, cur_item.top))
            self.prev_item = cur_item
            if not self.skip:
                if self.in_width:
                    self.source_point = self.prev_item.right
                else:
                    self.source_point = self.prev_item.bottom
            if is_cc_node(node) or is_bin_node(node):
                self.prev_type = node.bin.bin_type
            self.skip = False

    def createItem(self, node):
        item = None
        if is_bin_node(node):
            h, w, d = node.bin.size
            size = f'{round(h, 1)}x{round(w, 1)}x{round(d, 1)}'
            type = node.bin.bin_type
            if type == BinType.ingot:
                item = PlateGraphicsItem(
                    'Слиток\n' + size,
                    self.x, self.y, clr=QColor(200, 100, 100)
                )
                self.changePos()
            elif type == BinType.leaf or \
                    type == BinType.semifinished or\
                    type == BinType.INTERMEDIATE:
                if is_op_node(node.parent) and node.parent.operation == Operations.cutting:
                    self.in_width = False
                    self.changePos(residue=True)
                item = PlateGraphicsItem(
                    'Лист\n' + size, self.x, self.y
                )
                self.changePos()
            elif type == BinType.adjacent:
                item = PlateGraphicsItem(
                    'Смежный остаток\n' + size,
                    self.x, self.y, clr=QColor(100, 200, 100)
                )
                self.changePos()
            elif type == BinType.residue:
                item = PlateGraphicsItem(
                    'Остаток\n' + size,
                    self.x, self.y, clr=QColor(200, 200, 100)
                )
                self.changePos()
        elif is_op_node(node):
            item = OperationGraphicsItem(
                self.x, self.y, node.operation
            )
            if node.operation == Operations.cutting:
                self.cutting_nodes.append(item)
            self.changePos(operation=True)
        elif is_cc_node(node):
            number = node.result.qty()
            efficiency = round(node.result.efficiency() * 100, 2)
            correct_case = ' заготовка\n' if number == 1 else ' заготовки\n'
            item = PlateGraphicsItem(
                str(number) + correct_case + str(efficiency) + '%',
                self.x, self.y, clr=QColor(100, 200, 200)
            )
            self.scene.addItem(Edge(self.source_point, item.top))
            self.changePos(residue=True, pop=True)
        return item

    def changePos(self, operation=False, residue=False, pop=False):
        """Смена позиции в зависимости от типа созданного блока.

        Если `in_width` = True, т.е. всё ещё строится главная ветка, то блоки
        располагаются горизонтально и меняется только координата по иксу.
        Если `in_width` = False, т.е. строится одна из побочных веток, то
        элемнеты располагаются горизонтально и меняется координата по игреку.
        Если `residue` = True, т.е. только сменилось положение ветки, то нужно
        поменять координату по иксу на координату родительского узла.
        Если `pop` = True, т.е. нужно снять со стека один узел разреза, то мы
        его удаляем и ставим пропуск `skip` = True для того, чтобы не рисовать
        ребро из нижнего узла с упаковкой в узел с листом.
        Если operation = True, то сейчас вставлен блок операции, а его ширина
        меньше блока с контейнером.

        :param operation: Флаг операции с меньшей шириной, defaults to False
        :type operation: bool, optional
        :param residue: Флаг перехода на новую ветку, defaults to False
        :type residue: bool, optional
        :param pop: Флаг удаления узла разреза из стека, defaults to False
        :type pop: bool, optional
        """
        if self.in_width:
            self.x += 80 if operation else 140
        else:
            self.y += 80
        if pop:
            self.skip = True
            self.cutting_nodes.pop()
        if residue:
            try:
                self.source_point = self.cutting_nodes[-1].bottom
                self.y = 80
                self.x = self.cutting_nodes[-1].x_pos - 30
            except IndexError:
                pass
