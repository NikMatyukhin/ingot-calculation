"""Модуль визуализации схемы раскроя

:Date: 20.08.2020
:Version: 0.1
:Authors:
    - Воронов Владимир Сергеевич
"""

from random import random
from itertools import accumulate
from sequential_mh.tsh.rect import RectangleType

import matplotlib.pyplot as plt
import matplotlib.patches as patches


def patch_rect(axis, point, width, height, **kwargs):
    """Создание прямоугольника

    :param axis: ось
    :type axis: matplotlib.axes._subplots.AxesSubplot
    :param point: опорная точка (левый нижний угол)
    :type point: tuple[Number, Number]
    :param width: ширина прямоугольника
    :type width: int или float
    :param height: высота прямоугольника
    :type height: int или float
    """
    obj = axis.add_patch(
        patches.Rectangle(point, width, height, **kwargs)
    )
    return obj


def visualize(main_region, rectangles, tailings, xlim=10, ylim=10):
    """Визуализация схемы раскроя

    :param main_region: регион раскроя
    :type main_region: [type]
    :param rectangles: набор прямоугольников
    :type rectangles: list[PackedBlank]
    :param tailings: набор остатков
    :type tailings: list[Tailing]
    :param xlim: ограничение по оси X, defaults to 10
    :type xlim: int, optional
    :param ylim: ограничение по оси Y, defaults to 10
    :type ylim: int, optional
    """
    _, axes = plt.subplots()
    axes.set_xlim([0, xlim])
    axes.set_ylim([0, ylim])
    for rect in rectangles:
        patch_rect(
            axes, (rect.x, rect.y), rect.rectangle.width,
            rect.rectangle.length,
            color=(random(), random(), random()), ec='k', lw=0.5
        )
    y = []
    x = list(accumulate([main_region.max_width/100 for _ in range(100)]))
    if x[-1] > main_region.max_width:
        x[-1] = main_region.max_width
    for i in x:
        dist = main_region(i, 0, False)
        if dist is None:
            y.append(0)
        else:
            y.append(dist[1])

    axes.plot(x, y, c='b')
    y = list(accumulate([main_region.min_length/100 for i in range(100)]))
    if y[-1] > main_region.min_length:
        y[-1] = main_region.min_length
    axes.plot([main_region.max_width for _ in range(len(y))], y, c='b')

    for rect in tailings:
        if hasattr(rect, 'blp'):
            if rect.rtype == RectangleType.ALLOWANCE:
                edgecolor = "b"
                hatch = "X"
            elif rect.rtype == RectangleType.RESIDUAL:
                edgecolor = "k"
                hatch = r"\\"
            elif rect.rtype == RectangleType.END:
                edgecolor = "g"
                hatch = r"\\"
            else:
                edgecolor = "r"
                hatch = "//"
            patch_rect(
                axes, (rect.blp.x, rect.blp.y), rect.width, rect.length,
                facecolor='none', hatch=hatch, edgecolor=edgecolor, lw=0.5
            )
        else:
            patch_rect(
                axes, (rect.x, rect.y), rect.width, rect.length,
                facecolor='none', hatch="//", lw=0.5
            )
    plt.show()
