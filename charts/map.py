import math
from typing import Any, List, Union

import application_rc

from PyQt5.QtWidgets import (
    QGraphicsItem, QGraphicsScene, QWidget, QStyleOptionGraphicsItem
)
from PyQt5.QtCore import Qt, QRectF, QPointF, QLineF, QSizeF
from PyQt5.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QFontMetrics, QPixmap,
    QPolygonF, QIcon
)
from sequential_mh.bpp_dsc.tree import (
    BinNode, CuttingChartNode, OperationNode, Operations, Tree,
    is_op_node, is_bin_node, is_cc_node
)
from sequential_mh.bpp_dsc.rectangle import (
    BinType
)
from sequential_mh.bpp_dsc.support import dfs


class PlateGraphicsItem(QGraphicsItem):
    def __init__(self, txt, x, y, clr=QColor(255, 255, 255)):
        super().__init__()
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


class OperationGraphicsItem(QGraphicsItem):
    def __init__(self, x, y, type_):
        super().__init__()
        self.x_pos = x
        self.y_pos = y
        self.radius = 30
        self.width = self.radius * 2
        self.height = self.radius * 2
        self.color = QColor(100, 100, 150)
        self.type = type_

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
    """???????????????????? ?????????????????? - ?????????? ?????????? ?????????? ?????????????? ????????????????????????-??????????????

    :param QGraphicsItem: ???????????????????????? ?????????? ???????? ?????????????????? ??????????????????
    :type QGraphicsItem: class
    """
    def __init__(self, source: QPointF, dest: QPointF):
        super().__init__()
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
        angle = math.atan2(-line.dy(), line.dx())

        destArrowP1 = self.destPoint + QPointF(
            math.sin(angle - math.pi / 3) * self.arrowSize,
            math.cos(angle - math.pi / 3) * self.arrowSize
        )
        destArrowP2 = self.destPoint + QPointF(
            math.sin(angle - math.pi + math.pi / 3) * self.arrowSize,
            math.cos(angle - math.pi + math.pi / 3) * self.arrowSize
        )

        painter.setBrush(Qt.black)
        painter.drawPolygon(QPolygonF([line.p2(), destArrowP1, destArrowP2]))


class CuttingMapPainter:
    """???????????????????? ?????????? ??????????????

    ???? ???????????????????? ?????????? ?????????? ?????????????????? ???????? ?????????????????????? ???????????????????? ????????????????????
    ?????????? ??????????????. ?????????? ???????????? ?????????????? ???????????????????????????? ?? ??????????????. ????????????????
    ???????????? ?????????????? ???????????? ?? ???? ?????????????????? ?????????????????? ????????????????.
    """
    def __init__(self, scene: QGraphicsScene):
        self.scene = scene
        self.font = QFont('Segoe UI', 9)

    def setTree(self, tree: Tree):
        self.tree: Tree = tree

    def setEfficiency(self, efficiency: Any):
        if isinstance(efficiency, str) and efficiency.endswith('%'):
            efficiency = float(efficiency[:-1])
        self.efficiency: float = efficiency

    def drawTree(self):
        self.cutting_nodes: List[Operations] = []
        self.x = 0.0
        self.y = 0.0
        self.prev_item = None
        self.prev_type = None
        self.source_point = None
        self.in_width = True
        self.skip = False
        self.skip_counter = 0
        tree_path = list(dfs(self.tree.root))
        for index, node in enumerate(tree_path):
            if is_op_node(node):
               if node.operation == Operations.rolling:
                    continue
            if self.skip_counter > 0:
                self.skip_counter -= 1
                continue
            try:
                op_node = tree_path[index + 1]
                next_node = tree_path[index + 3]
                if is_bin_node(node) and is_bin_node(next_node) and is_op_node(op_node) and not op_node.operation == Operations.cutting:
                    if node.bin.size == next_node.bin.size:
                        self.skip_counter = 2
            except IndexError:
                pass
            cur_item = self.createItem(node)
            if not cur_item:
                continue
            self.scene.addItem(cur_item)
            if is_bin_node(node):
                if node.bin.bin_type == BinType.ingot:
                    efficiency = self.scene.addText(
                        f'?????????? ??????????????:\n {self.efficiency:.2f}%'
                    )
                    efficiency.setX(self.x - 140)
                    efficiency.setY(self.y - 60)
            if is_op_node(node):
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

    def createItem(self, node: Union[BinNode, OperationNode, CuttingChartNode]):
        item = None
        if is_bin_node(node):
            node: BinNode
            h, w, d = node.bin.size
            size = f'{math.ceil(h)}x{math.ceil(w)}x{round(d, 2)}'
            type = node.bin.bin_type
            if type == BinType.ingot:
                item = PlateGraphicsItem(
                    '????????????\n' + size,
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
                    '????????\n' + size, self.x, self.y
                )
                self.changePos()
            elif type == BinType.adjacent:
                item = PlateGraphicsItem(
                    '?????????????? ??????????????\n' + size,
                    self.x, self.y, clr=QColor(100, 200, 100)
                )
                self.changePos()
            elif type == BinType.residue:
                item = PlateGraphicsItem(
                    '??????????????\n' + size,
                    self.x, self.y, clr=QColor(200, 200, 100)
                )
                self.changePos()
            else:
                item = PlateGraphicsItem(
                    '????????\n' + size, self.x, self.y
                )
                self.changePos()
        elif is_op_node(node):
            node: OperationNode
            item = OperationGraphicsItem(
                self.x, self.y, node.operation
            )
            if node.operation == Operations.cutting:
                self.cutting_nodes.append(item)
            self.changePos(operation=True)
        elif is_cc_node(node):
            node: CuttingChartNode
            number = node.result.qty()
            efficiency = round(node.efficiency() * 100, 2)
            correct_case = ' ??????????????????\n' if number == 1 else ' ??????????????????\n'
            item = PlateGraphicsItem(
                str(number) + correct_case + str(efficiency) + '%',
                self.x, self.y, clr=QColor(100, 200, 200)
            )
            self.scene.addItem(Edge(self.source_point, item.top))
            self.changePos(residue=True, pop=True)
        else:
            item = PlateGraphicsItem(
                '????????\n' + '???????????? ??????????????!', self.x, self.y
            )
            self.changePos()
        return item

    def changePos(self, operation: bool = False, residue: bool = False,
                  pop: bool = False):
        """?????????? ?????????????? ?? ?????????????????????? ???? ???????? ???????????????????? ??????????.

        ???????? `in_width` = True, ??.??. ?????? ?????? ???????????????? ?????????????? ??????????, ???? ??????????
        ?????????????????????????? ?????????????????????????? ?? ???????????????? ???????????? ???????????????????? ???? ????????.
        ???????? `in_width` = False, ??.??. ???????????????? ???????? ???? ???????????????? ??????????, ????
        ???????????????? ?????????????????????????? ?????????????????????????? ?? ???????????????? ???????????????????? ???? ????????????.
        ???????? `residue` = True, ??.??. ???????????? ?????????????????? ?????????????????? ??????????, ???? ??????????
        ???????????????? ???????????????????? ???? ???????? ???? ???????????????????? ?????????????????????????? ????????.
        ???????? `pop` = True, ??.??. ?????????? ?????????? ???? ?????????? ???????? ???????? ??????????????, ???? ????
        ?????? ?????????????? ?? ???????????? ?????????????? `skip` = True ?????? ????????, ?????????? ???? ????????????????
        ?????????? ???? ?????????????? ???????? ?? ?????????????????? ?? ???????? ?? ????????????.
        ???????? operation = True, ???? ???????????? ???????????????? ???????? ????????????????, ?? ?????? ????????????
        ???????????? ?????????? ?? ??????????????????????.

        :param operation: ???????? ???????????????? ?? ?????????????? ??????????????, defaults to False
        :type operation: bool, optional
        :param residue: ???????? ???????????????? ???? ?????????? ??????????, defaults to False
        :type residue: bool, optional
        :param pop: ???????? ???????????????? ???????? ?????????????? ???? ??????????, defaults to False
        :type pop: bool, optional
        """
        if self.in_width:
            self.x += 80 if operation else 140
        else:
            self.y += 80
        if pop:
            self.skip = True
            try:
                self.cutting_nodes.pop()
            except IndexError:
                pass
        if residue:
            try:
                self.source_point = self.cutting_nodes[-1].bottom
                self.y = 100
                self.x = self.cutting_nodes[-1].x_pos - 30
            except IndexError:
                pass
