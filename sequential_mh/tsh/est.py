"""Модуль описания области с изменяющимися размерами

:Date: 12.03.2021
:Version: 0.1
:Authors:
    - Воронов Владимир Сергеевич
"""

import math
from typing import Optional

from .protocols import Number, Vec2
from .rect import Point, min_enclosing_rect


class Estimator:
    def __init__(self, rectangle, height, g_height, start=None, limits=None,
                 x_hem=None, y_hem=None):
        self.rectangle = rectangle
        self.height = round(height, 4)
        self.g_height = g_height
        if start is None:
            start = self.rectangle.blp

        self.start = Point(*start)
        self._limits = limits
        if x_hem is None:
            x_hem = (0, 0)
        if y_hem is None:
            y_hem = (0, 0)
        self._x_hem = x_hem  # кромка по ширине (X) (левая, правая)
        self._y_hem = y_hem  # кромка по длине (Y) (нижняя, верхняя)

    def update(self, rectangle, with_lim=True):
        x, y = rectangle.trp
        min_rect = min_enclosing_rect((self.rectangle, rectangle))
        if min_rect == self.rectangle:
            dist = self(*rectangle.trp, with_lim=with_lim)
        else:
            dist = self(*min_rect.trp, with_lim=with_lim)
        if dist is None:
            raise ValueError(f'Точка {(x, y)} лежит вне области')
        volume = self.rectangle.length * self.rectangle.width * self.height
        new_height = volume / (min_rect.length * min_rect.width)
        self.rectangle = min_rect
        self.height = new_height

    def cut(self, point=None):
        x_0, _ = self.rectangle.blp
        if point is None:
            x, y = self.rectangle.trp
        else:
            x, y = point
        dist = self(x, y)
        # print(x, y, dist)
        if x == 0 and y == 0:
            return [self]
        if dist is None:
            raise ValueError(f'Точка {(x, y)} лежит вне области')
        w_max, l_max = dist
        args = self.rectangle, self.height, self.g_height
        if w_max == 0 and l_max == 0:
            return []
        if w_max == 0:
            return [
                self.__class__(
                    *args, start=Point(self.start[0], y), limits=self.limits,
                    x_hem=self._x_hem, y_hem=(0, self.top_hem)
                )
            ]
        if l_max == 0:
            return [
                self.__class__(
                    *args, start=Point(x, self.start[1]), limits=self.limits,
                    x_hem=(0, self.right_hem), y_hem=self._y_hem
                )
            ]
        # вертикальный разрез
        if self.w_lim >= x - self.start.x:
            w_lim = x - self.start.x
        else:
            w_lim = x - x_0 if self.w_lim == 0 else min(self.w_lim, x) - x_0
        if self.l_lim == 0:
            l_lim = 0
        else:
            l_lim = self.start.y + self.l_lim - y
        est1 = self.__class__(
            *args, start=Point(self.start.x, y),
            limits=(l_lim, w_lim),
            x_hem=self._x_hem, y_hem=self._y_hem
        )
        if 0 < self.w_lim < x - self.start.x:
            new_x = min(self.w_lim, x)
        else:
            new_x = x
        est2 = self.__class__(
            *args, start=Point(new_x, self.start.y),
            limits=self.get_new_limits(x, self.start.y),
            x_hem=self._x_hem, y_hem=self._y_hem
        )
        # горизонтальный разрез
        if self.w_lim == 0:
            w_lim = 0
        else:
            w_lim = self.get_new_limits(x, self.start.y)[1]
        if self.l_lim == 0 or self.l_lim >= y - self.start.y:
            l_lim = y - self.start.y
        else:
            l_lim = self.get_new_limits(self.start.x, y)[0]
        est3 = self.__class__(
            *args, start=Point(self.start.x, y),
            limits=self.get_new_limits(self.start.x, y),
            x_hem=self._x_hem, y_hem=self._y_hem
        )
        est4 = self.__class__(
            *args, start=Point(new_x, self.start.y),
            limits=(l_lim, w_lim),
            x_hem=self._x_hem, y_hem=self._y_hem
        )
        return [est1, est2, est3, est4]

    def _estimate_max_len(self, x, y, with_lim=True) -> Optional[Vec2]:
        x_1, y_1 = self.tlp
        x_2, y_2 = self.trp
        width = length = None

        if less_or_equal(x, x_1) and less_or_equal(y, y_2):
            width, length = x_2 - x, y_1 - y
        elif less_or_equal(x, x_1) and y_2 < y and less_or_equal(y, y_1):
            width = y_2 * x_1 * self.height / (self.g_height * y) - x
            length = y_1 - y
        elif x_1 < x and less_or_equal(x, x_2) and less_or_equal(y, y_2):
            width = x_2 - x
            length = y_2 * x_1 * self.height / (self.g_height * x) - y
        elif x_1 < x < x_2 and y_2 < y < y_1 and y <= y_2 * x_1 * self.height / (self.g_height * x):
            width = y_2 * x_1 * self.height / (self.g_height * y) - x
            length = y_2 * x_1 * self.height / (self.g_height * x) - y

        if width is None or length is None:
            return None
        if with_lim:
            right_hem, top_hem = self.estimate_hem_end(x, y)
            if right_hem is None or top_hem is None:
                return None
            if self.w_lim > 0:
                x_lim = self.start.x + self.w_lim
                if x > x_lim:
                    width = None
                else:
                    width = min(x_lim - x, width - right_hem)
            if self.l_lim > 0:
                y_lim = self.start.y + self.l_lim
                if y > y_lim:
                    length = None
                else:
                    length = min(y_lim - y, length - top_hem)
        if width is None or length is None:
            return None
        return width, length

    def estimate_hem_end(self, x, y):
        def curve_value(x_, y_):
            return y_1 * x_1 * self.height / (self.g_height * x_) - y_
        x_1, y_1 = self.tlp.x, self.trp.y
        x_correction = 0
        y_correction = 0
        if math.isclose(self.height, self.g_height, rel_tol=1e-4):
            x_correction = self.right_hem
            y_correction = self.top_hem
        if less_or_equal(x, x_1 - x_correction):
            x = x_1 - x_correction
        if less_or_equal(y, y_1 - y_correction):
            y = y_1 - y_correction
        y_est = round(curve_value(x, y), 4)
        x_est = round(curve_value(y, x), 4)
        if y_est < 0 or x_est < 0:
            return None, None
        min_y_est = round(curve_value(x + self.right_hem, y + self.top_hem), 4)
        min_x_est = round(curve_value(y + self.top_hem, x + self.right_hem), 4)
        if min_y_est < 0 or min_x_est < 0:
            return None, None
        top_hem = y_est - min_y_est
        right_hem = x_est - min_x_est
        return right_hem, top_hem

    def get_new_limits(self, x, y):
        if self.l_lim > 0:
            l_lim = self.start.y + self.l_lim - y
        else:
            l_lim = 0
        if self.w_lim == 0:
            w_lim = 0
        elif self.w_lim <= x - self.start.x:
            w_lim = 0
        else:
            w_lim = self.start.x + self.w_lim - x
        return l_lim, w_lim

    @property
    def w_lim(self) -> Number:
        """Ширина области с учетом ограничений"""
        if self._limits and 0 < self._limits[1] < self.trp.x - self.start.x:
            return self._limits[1]
        return self.max_width

    @property
    def l_lim(self) -> Number:
        """Длина области с учетом ограничений"""
        if self._limits and 0 < self._limits[0] < self.tlp.y - self.start.y:
            return self._limits[0]
        return self.max_length

    @property
    def right_hem(self) -> Number:
        """Правая кромка"""
        return self._x_hem[1]

    @property
    def left_hem(self) -> Number:
        """Левая кромка"""
        return self._x_hem[0]

    @property
    def bottom_hem(self) -> Number:
        """Нижняя кромка"""
        return self._y_hem[0]

    @property
    def top_hem(self) -> Number:
        """Верхняя кромка"""
        return self._y_hem[1]

    @property
    def max_length(self) -> Number:
        """Максимальная длина"""
        length = self.rectangle.length * self.height / self.g_height
        return length - self.start.y + self.rectangle.blp.y

    @property
    def max_length_lim(self) -> Number:
        """Максимальная длина с учетом ограничений"""
        # length = self.rectangle.length * self.height / self.g_height
        length = self.max_length
        if length > self.l_lim:  #  + self.start.y:
            return self.l_lim
        return length

    @property
    def limits(self):
        """Ограничения"""
        return self._limits

    @property
    def max_width(self) -> Number:
        """Максимальная ширина"""
        width = self.rectangle.width * self.height / self.g_height
        return width - self.start.x + self.rectangle.blp.x

    @property
    def max_width_lim(self) -> Number:
        """Максимальная ширина с учетом ограничений"""
        # width = self.rectangle.width * self.height / self.g_height
        width = self.max_width
        if width > self.w_lim:  # + self.start.x:
            return self.w_lim
        return width

    @property
    def min_length(self) -> Number:
        """Минимальная длина"""
        _, y = self.rectangle.trp
        return y - self.start.y + self.rectangle.blp.y

    @property
    def min_length_lim(self) -> Number:
        """Минимальная длина с учетом ограничений"""
        # _, y = self.rectangle.trp
        length = self.min_length
        if length > self.l_lim + self.start.y:
            return self.l_lim
        return length

    @property
    def min_width(self) -> Number:
        """Минимальная ширина"""
        x, _ = self.rectangle.trp
        return x - self.start.x + self.rectangle.blp.x

    @property
    def min_width_lim(self) -> Number:
        """Минимальная ширина с учетом ограничений"""
        # x, _ = self.rectangle.trp
        width = self.min_width
        if width > self.w_lim + self.start.x:
            return self.w_lim
        return width

    @property
    def tlp(self) -> Point:
        """Верхняя левая вершина"""
        x, _ = self.rectangle.blp
        return Point(
            # self.rectangle.width + x, self.max_length + y + self.start.y
            self.rectangle.width + x, self.max_length + self.start.y
        )

    @property
    def trp(self) -> Point:
        """Верхняя правая вершина"""
        _, y = self.rectangle.blp
        return Point(
            # self.max_width + x + self.start.x, self.rectangle.length + y
            self.max_width + self.start.x, self.rectangle.length + y
        )

    def __call__(self, x, y, with_lim=True):
        return self._estimate_max_len(x, y, with_lim=with_lim)

    def __repr__(self):
        return (
            f'{self.__class__.__name__}'
            f'({repr(self.rectangle)}, {self.height}, {self.g_height})'
        )


def less_or_equal(x, y, *, rel_tol=1e-5):
    """Операция меньше или равно для сравнения чисел типа float"""
    return x < y or math.isclose(x, y, rel_tol=rel_tol)
