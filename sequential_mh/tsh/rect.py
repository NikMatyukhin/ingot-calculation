"""Модуль классов прямоугольников для обеспечения работы алоритма

:Date: 10.01.2020
:Version: 0.1
:Authors:
    - Воронов Владимир Сергеевич
"""

from dataclasses import dataclass
from enum import Enum
from operator import attrgetter
from typing import Iterable, Optional, Union, NamedTuple

from .protocols import RectangleProtocol, Number, Vec2

Point = NamedTuple('Point', [('x', Number), ('y', Number)])
PointType = Union[tuple[Number, Number], Point]


class RectangleType(Enum):
    """Типы прямоугольников"""
    # основной прямоугольник
    RECTANGLE = 'Rectangle'
    # кромка
    EDGE = 'Edge'
    # припуск
    ALLOWANCE = 'Allowance'
    # торец
    END = 'End'
    # остаток
    RESIDUAL = 'Residual'
    # используемый остаток
    USED_RESIDUAL = 'Used residual'
    # не определен
    NOT_DETERMINED = 'NotDetermined'


class Rectangle:
    """Прямоугольник на плоскости"""
    def __init__(self, blp: PointType, trp: PointType, rtype=None):
        if isinstance(blp, tuple):
            blp = Point(*blp)
        if isinstance(trp, tuple):
            trp = Point(*trp)
        # нижняя левая точка
        self._blp: Point = min(blp, trp)
        # верхняя правая точка
        self._trp: Point = trp if self._blp is blp else blp
        if rtype is None:
            rtype = RectangleType.NOT_DETERMINED
        self.rtype = rtype

    def intersection(self, other: 'Rectangle') -> Optional['Rectangle']:
        """Пересечение двух прямоугольников

        :param other: второй прямоугольник
        :type other: Rectangle
        :return: прямоугольник, являющийся перемечением исходных
        :rtype: Rectangle
        """
        blp = Point(max(self.blp.x, other.blp.x), max(self.blp.y, other.blp.y))
        trp = Point(min(self.trp.x, other.trp.x), min(self.trp.y, other.trp.y))
        if blp.x < trp.x and blp.y < trp.y:
            return self.__class__(blp, trp)
        return None

    def intersection_square(self, other: 'Rectangle') -> Number:
        """Площадь пересечения двух прямоугольников

        :param other: второй прямоугольник
        :type other: Rectangle
        :return: площадь пересечения
        :rtype: Number
        """
        intersection = self.intersection(other)
        if intersection is None:
            return 0
        return intersection.square

    def cut(self, point: PointType):
        """Резка прямоугольника по точке"""
        if not self.point_in_rect(point):
            raise ValueError(f'Точка {point} лежит вне прямоугольника {self}')
        x, y = point
        x_min, y_min = self.blp
        x_max, y_max = self.trp
        if self.is_corner(point):
            # в углу
            return (self, )
        if x == x_min or x == x_max:
            # на правой или левой границе
            rect1 = self.__class__(self.blp, (x_max, y))
            rect2 = self.__class__((x_min, y), self.trp)
            return rect1, rect2
        if y == y_min or y == y_max:
            # на верхней или нижней границе
            rect1 = self.__class__(self.blp, (x, y_max))
            rect2 = self.__class__((x, y_min), self.trp)
            return rect1, rect2
        # внутри
        rect1 = self.__class__(self.blp, point)
        rect2 = self.__class__((x, y_min), (x_max, y))
        rect3 = self.__class__(point, self.trp)
        rect4 = self.__class__((x_min, y), (x, y_max))
        return rect1, rect2, rect3, rect4

    def inside_points(self, obj) -> list[Point]:
        """Вершины прямоугольника, лежащие строго внутри друого.

        Внутренние вершины определяются по строгому неравенству.
        Если вершина лежит на стороне другого прямоугольника,
        он не считается внутренним.

        :param obj: прямоугольник, вершины которого подлежат проверке
        :type obj: Rectangle
        :return: вершины, являющиеся внутренними
        :rtype: list[Point]
        """
        points = []
        x_min, y_min = self.blp
        x_max, y_max = self.trp
        for p in obj.corners:
            if x_min < p.x < x_max and y_min < p.y < y_max:
                points.append(p)
        return points

    def boundary_points(self, obj) -> list[Point]:
        """Вершины прямоугольника, лежащие на границах другого.

        Если вершина лежит на стороне другого прямоугольника,
        но не совпадает с его вершиной, он не считается внутренним.

        :param obj: прямоугольник, вершины которого подлежат проверке
        :type obj: Rectangle
        :return: вершины, лежащие на границах
        :rtype: list[Point]
        """
        points = []
        x_min, y_min = self.blp
        x_max, y_max = self.trp
        for p in obj.corners:
            if not self.is_corner(p):
                if p.x in (x_min, x_max) or p.y in (y_min, y_max):
                    points.append(p)
        return points

    def point_in_rect(self, point: PointType) -> bool:
        """Проверка точки на вхождение в прямоугольник.

        Если точка лежит внутри, на одной из сторон или совпадает с
        углом прямоугольника, она считается внутренней.

        :param point: точка, подлежащая проверке на вхождение
        :type point: Union[tuple[Number, Number], Point]
        :return: True, если точка лежит внутри прямоугольника
        :rtype: bool
        """
        x, y = point
        x_min, y_min = self.blp
        x_max, y_max = self.trp
        return x_min <= x <= x_max and y_min <= y <= y_max

    def is_corner(self, point: PointType) -> bool:
        """Проверка точки на совпадение с вершиной прямоугольника.

        :param point: точка, подлежащая проверке
        :type point: PointType
        :return: True, если точка является вершиной прямоугольника
        :rtype: bool
        """
        if isinstance(point, tuple):
            point = Point(*point)
        return point in self.corners

    def is_subrect(self, obj) -> bool:
        """Проверка прямоугольника на полное вхождение в другой прямоугольник.

        Проверяется вхождение левой нижней вершины и правой верхней вершины.

        :param obj: прямоугольник, подлежащий проверке
        :type obj: Rectangle
        :return: True, если прямоугольник является подпрямоугольником
        :rtype: bool
        """
        blp_o, trp_o = obj.blp, obj.trp
        return self.point_in_rect(blp_o) and self.point_in_rect(trp_o)

    @property
    def corners(self) -> tuple[Point, Point, Point, Point]:
        """Вершины прямоугольника

        :return: все вершины прямоугольника
        :rtype: tuple[Point, Point, Point, Point]
        """
        return self.blp, self.brp, self.trp, self.tlp

    @property
    def trp(self) -> Point:
        """Верхняя правая вершина"""
        return self._trp

    @property
    def tlp(self) -> Point:
        """Верхняя левая вершина"""
        return Point(self._blp[0], self._trp[1])

    @property
    def brp(self) -> Point:
        """Нижняя правая вершина"""
        return Point(self._trp[0], self._blp[1])

    @property
    def blp(self) -> Point:
        """Нижняя левая вершина"""
        return self._blp

    @blp.setter
    def blp(self, value):
        self._blp = value

    @property
    def x(self) -> Number:
        """Координата по оси X нижней левой вершины"""
        return self._blp.x

    @property
    def y(self) -> Number:
        """Координата по оси Y нижней левой вершины"""
        return self._blp.y

    @property
    def length(self) -> Number:
        """Длина прямоугольника"""
        return self.trp[1] - self.blp[1]

    @property
    def width(self) -> Number:
        """Ширина прямоугольника"""
        return self.trp[0] - self.blp[0]

    @property
    def min_side(self):
        """Минимальная сторона"""
        return min(self.length, self.width)

    @property
    def max_side(self):
        """Максимальная сторона"""
        return max(self.length, self.width)

    @property
    def square(self):
        """Площадь"""
        return self.length * self.width

    @classmethod
    def create_by_size(cls, blp: PointType, length: Number, width: Number):
        """Создание прямоугольника на основе вершины и размеров сторон

        :param blp: левая нижняя вершина
        :type blp: PointType
        :param length: длина прямоугольника
        :type length: Number
        :param width: ширина прямоугольника
        :type width: Number
        :return: новый прямоугольник с заданными размерами и положением
        :rtype: Rectangle
        """
        x, y = blp
        trp = x + width, y + length
        return cls(blp, trp)

    def __eq__(self, o) -> bool:
        return self.blp == o.blp and self.trp == o.trp

    __and__ = intersection

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({repr(self.blp)}, {repr(self.trp)})'


@dataclass
class PackedRectangle:
    """Упакованный прямоугольник

    :ivar rectangle: прямоугольник
    :vartype rectangle: RectangleProtocol
    :ivar x: координата x
    :vartype x: int или float
    :ivar y: координата y
    :vartype y: int или float
    """
    rectangle: RectangleProtocol
    x: Number
    y: Number

    @property
    def coordinates(self) -> Vec2:
        """Координаты в виде кортежа"""
        return self.x, self.y


def min_enclosing_rect(rectangles: Iterable[Rectangle]) -> Rectangle:
    """Минимальный объемлющий прямоугольник

    Минимальный прямоугольник, который содержит заданный набор прямоугольников.

    :param rectangles: набор прямоугольников
    :type rectangles: Iterable[Rectangle]
    :return: минимальный объемлющий прямоугольник
    :rtype: Rectangle
    """
    x = min(map(attrgetter('blp.x'), rectangles))
    y = min(map(attrgetter('blp.y'), rectangles))
    blp = Point(x, y)
    x = max(map(attrgetter('trp.x'), rectangles))
    y = max(map(attrgetter('trp.y'), rectangles))
    trp = Point(x, y)
    return Rectangle(blp, trp)


def difference_rect(dst: Rectangle, src: list[Rectangle]) -> list[Rectangle]:
    # TODO: переделать на более адекватный вариант
    # https://stackoverflow.com/questions/25068538/intersection-and-difference-of-two-rectangles
    """Разность областей прямоугольников

    Определяется область в исходном прямоугольнике не занятая другими
    прямоугольниками.

    :param dst: исходный прямоугольник
    :type dst: Rectangle
    :param src: набор прямоугольников, которые будут "вычитаться" из
                исходного
    :type src: list[Rectangle]
    :return: набор свободных областей
    :rtype: list[Rectangle]
    """
    region = [dst]
    src.sort(key=lambda item: len(dst.inside_points(item)))
    for r in src:
        rdst = region.pop(0)
        inside_points = rdst.inside_points(r)
        if inside_points:
            point = inside_points[0]
            rectangles = rdst.cut(point)
            region = [item for item in rectangles if r != item]
        else:
            boundary_points = rdst.boundary_points(r)
            if boundary_points:
                point = boundary_points[0]
                rectangles = rdst.cut(point)
                region = [item for item in rectangles if r != item]
            else:
                return []
        i = 0
        while i < len(region):
            if r.is_subrect(region[i]):
                region.pop(i)
            else:
                i += 1
    return region
