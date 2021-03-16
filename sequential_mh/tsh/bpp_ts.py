"""Алгоритм раскроя в две стороны

:Date: 10.02.2020
:Version: 0.1
:Authors:
    - Воронов Владимир Сергеевич
"""

from copy import deepcopy
from itertools import chain
from operator import itemgetter
from typing import NamedTuple

from .protocols import Number, RectangleProtocol
from .support import (
    delete_from_dict, dict_to_list, exclude_from_dict, is_empty_dict
)
from .rect import (
    Point, Rectangle, PackedRectangle, difference_rect, min_enclosing_rect
)
from .ph import ph_bpp, rotate_all
from .visualize import visualize
from .est import Estimator


StateLayout = NamedTuple(
    'StateLayout',
    [
        ('blanks', list[PackedRectangle]),
        ('unplaced', list[RectangleProtocol]),
        ('tailings', list[Rectangle]),
        ('min_rect', Rectangle),
        ('efficiency', Number),
        ('inters_square', Number),
        ('aspect_ratio', Number)
    ]
)


def bpp_ts(length, width, height, g_height, rectangles, first_priority=False,
           hem=(0, 0), allowance=0, max_size=None, is_visualize=False):
    # rectangles - список прямоугольников
    # rectangles.sort()
    src_rect = Rectangle((0, 0), (width, length))
    min_rect = Rectangle((0, 0), (0, 0))

    main_region = Estimator(
        src_rect, height, g_height, limits=max_size,
        x_hem=(hem[1], hem[1]), y_hem=(hem[0], hem[0])
    )
    all_regions = [main_region]
    result, unplaced, all_tailings = [], [], []
    rotate_all(rectangles)
    while not is_empty_dict(rectangles):  # проходиться по индексам
        layout_options = []
        if not all_regions:
            unplaced.extend(dict_to_list(rectangles))
            break
        for i, region in enumerate(all_regions):
            print(f'стартовая точка региона {i}: {region.start}')
            tailings = []
            if first_priority:
                for_packing = rectangles[first_priority]
            else:
                for_packing = dict_to_list(rectangles)
            variant, _, best = get_best_fig(
                for_packing, region, main_region.rectangle,
                hem, allowance, *region.start
            )
            if best is None:
                continue
            if variant == 15:
                state = StateLayout([], [best], [], min_rect, 0, 0, 0)
                layout_options.append(state)
                continue

            dummy_hem = dummy_alw = None
            new_start = region.start
            # FIXME: переписать следующий кусок
            # создание фиктивных прямоугольников под кромки и припуски
            if region.start.x == 0:
                if region.right_hem > 0:
                    # кромка справа и слева
                    dummy_hem = Rectangle.create_by_size(
                        region.start, best.length + allowance, region.right_hem
                    )
                    new_start = Point(region.right_hem, region.start.y)
                    tailings.append(dummy_hem)
                if allowance:
                    # горизонтальный припуск
                    dummy_alw = Rectangle.create_by_size(
                        new_start, allowance, best.width
                    )
                    new_start = Point(region.right_hem, new_start.y + allowance)
                    tailings.append(dummy_alw)
            elif region.start.y == 0:
                if region.bottom_hem > 0:
                    # кромка сверху и снизу
                    dummy_hem = Rectangle.create_by_size(
                        region.start, region.bottom_hem, best.width + allowance
                    )
                    new_start = Point(region.start.x, region.bottom_hem)
                    tailings.append(dummy_hem)
                if allowance:
                    # вертикальный припуск
                    dummy_alw = Rectangle.create_by_size(
                        new_start, best.length, allowance
                    )
                    new_start = Point(new_start.x + allowance, new_start.y)
                    tailings.append(dummy_alw)
            blanks = [PackedRectangle(deepcopy(best), *new_start)]
            rect = Rectangle.create_by_size(new_start, best.length, best.width)
            if dummy_alw:
                rect = min_enclosing_rect((dummy_alw, rect))
            if dummy_hem:
                rect = min_enclosing_rect((dummy_hem, rect))
            new_min_rect = min_enclosing_rect((min_rect, rect))
            empty_rect = difference_rect(new_min_rect, [min_rect, rect])
            square, usable_square = rect.square, best.area
            if dummy_hem:
                usable_square += dummy_hem.square
            if dummy_alw:
                usable_square += dummy_alw.square
            intersection_square = rect.intersection_square(src_rect)

            if empty_rect:
                empty_rect = empty_rect[0]
                square += empty_rect.square
                res, *_, _tailings = ph_bpp(
                    empty_rect.length, empty_rect.width,
                    deepcopy(exclude_from_dict(best, rectangles)),
                    *empty_rect.blp, first_priority=False,
                    sorting='width'
                )
                tailings.extend(_tailings)
                placed_blanks = list(chain.from_iterable(res.values()))
                if placed_blanks:
                    # usable_square += sum(b.blank.area for b in placed_blanks)
                    usable_square += sum(b.rectangle.area for b in placed_blanks)
                    blanks.extend(placed_blanks)
                else:
                    tailings.append(Rectangle.create_by_size(empty_rect.blp, empty_rect.length, empty_rect.width))
            status = StateLayout(
                blanks, [], tailings, new_min_rect,
                usable_square / square,  intersection_square,
                new_min_rect.min_side / new_min_rect.max_side
            )
            layout_options.append(status)
            print(f'Остатки региона {i}: {tailings}')
        # выбрать вариант размещения
        layout = max(
            enumerate(layout_options), key=lambda item: (item[1].efficiency,
                                              item[1].inters_square,
                                              item[1].aspect_ratio)
        )
        print('Выбор:', layout[0])
        layout = layout[1]
        # добавляю размещенные заготовки в результат
        result.extend(layout.blanks)
        unplaced.extend(layout.unplaced)
        all_tailings.extend(layout.tailings)
        # удаляю из набора
        delete_from_dict([b.rectangle for b in layout.blanks], rectangles)
        delete_from_dict(layout.unplaced, rectangles)
        # обновить min_rect
        min_rect = layout.min_rect
        # обновить region
        # TODO: неправильно обновляется, когда min_rect меньше исходного
        if min_rect.length > 0 and min_rect.width > 0:
            main_region.update(min_rect)
        # обновить регионы
        print(f'Точка реза: {min_rect.trp}')
        all_regions = main_region.cut(point=min_rect.trp)

        if is_visualize:
            l_max = length * height / g_height
            w_max = width * height / g_height
            visualize(main_region, result, all_tailings,
                      xlim=w_max, ylim=l_max)

    if min_rect.length > 0 and min_rect.width > 0:
        if hem[1] > 0:
            dummy = Rectangle.create_by_size(min_rect.brp, min_rect.length, hem[1])
            all_tailings.append(dummy)
            dummy = Rectangle.create_by_size(min_rect.brp, min_rect.length, hem[1])
            new_min_rect = min_enclosing_rect((min_rect, dummy))
            main_region.update(new_min_rect, with_lim=False)
        if hem[0] > 0:
            dummy = Rectangle.create_by_size(min_rect.tlp, hem[0], min_rect.width)
            all_tailings.append(dummy)
            dummy = Rectangle.create_by_size(min_rect.tlp, hem[0], min_rect.width)
            new_min_rect = min_enclosing_rect((min_rect, dummy))
            main_region.update(new_min_rect, with_lim=False)

    if main_region.rectangle != src_rect:
        rect = min_enclosing_rect((main_region.rectangle, src_rect))
        if rect.length > 0 and rect.width > 0:
            main_region.update(rect, with_lim=False)

    print(f'Остатки: {all_tailings}')
    return src_rect, main_region, result, unplaced, all_tailings


def get_best_fig(rectangles, estimator, src_rect,
                 hem, allowance=0, x0=0, y0=0):
    priority, orientation, best = 16, None, None
    # w_0 = estimator.min_width
    # l_0 = estimator.min_length
    # w_max = estimator.max_width
    w_0 = estimator.min_width_lim
    l_0 = estimator.min_length_lim
    w_max = estimator.max_width_lim
    if x0 == 0 and hem[1] > 0:
        # кромка справа и слева
        x0 += hem[1]
    elif y0 == 0 and hem[0] > 0:
        # кромка сверху и снизу
        y0 += hem[0]
    # для припуска
    if x0 in (0, hem[1]):
        y0 += allowance
    elif y0 in (0, hem[0]):
        x0 += allowance
    for rect in rectangles:
        size = rect.size[:-1]
        for j in range(1 + rect.is_rotatable):
            rect_w = size[(1 + j) % 2]
            rect_l = size[(0 + j) % 2]
            dist = estimator(x0 + rect_w, y0)
            if dist is None:
                priority, orientation, best = 15, j, rect
                continue
            _, l_max = dist

            if priority > 1 and rect_w == w_0 and rect_l == l_max:
                # вариант 1
                priority, orientation, best = 1, j, rect
            elif priority > 2 and rect_w == w_max and rect_l == l_max:
                # вариант 2
                priority, orientation, best = 2, j, rect
            elif priority > 3 and w_0 < rect_w < w_max and rect_l == l_max:
                # вариант 3
                priority, orientation, best = 3, j, rect
            elif priority > 4 and rect_w < w_0 and rect_l == l_max:
                # вариант 4
                priority, orientation, best = 4, j, rect
            elif priority > 5 and rect_w == w_max and rect_l < l_max:
                # вариант 5
                priority, orientation, best = 5, j, rect
            elif priority > 6 and rect_w == w_0 and rect_l == l_0:
                # вариант 10
                priority, orientation, best = 6, j, rect
            elif priority > 7 and rect_w == w_0 and rect_l < l_0:
                # вариант 8
                priority, orientation, best = 7, j, rect
            elif priority > 8 and rect_w < w_0 and rect_l == l_0:
                # вариант 9
                priority, orientation, best = 8, j, rect
            elif priority > 9 and rect_w == w_0 and l_0 < rect_l < l_max:
                # вариант 6
                priority, orientation, best = 9, j, rect
            elif priority > 10 and w_0 < rect_w < w_max and rect_l == l_0:
                # вариант 7
                priority, orientation, best = 10, j, rect
            elif priority > 11 and w_0 < rect_w < w_max and l_0 < rect_l < l_max:
                # вариант 11
                priority, orientation, best = 11, j, rect
            elif priority > 12 and rect_w < w_0 and l_0 < rect_l < l_max:
                # вариант 12
                priority, orientation, best = 12, j, rect
            elif priority > 13 and w_0 < rect_w < w_max and rect_l < l_0:
                # вариант 13
                priority, orientation, best = 13, j, rect
            elif priority > 14 and rect_w < w_0 and rect_l < l_0:
                # вариант 14
                priority, orientation, best = 14, j, rect
            elif priority > 15:
                # ничего не входит
                priority, orientation, best = 15, j, rect
    if best and orientation == 1 and best.is_rotatable:
        best.rotate()
    if 11 <= priority < 15 and best:
        size = best.size[:-1]
        variants = []
        for j in range(1 + best.is_rotatable):
            rect_w = size[(1 + j) % 2]
            rect_l = size[(0 + j) % 2]
            dist = estimator(x0 + rect_w, y0)
            if dist and rect_l <= dist[1]:
                rect = Rectangle.create_by_size(estimator.start, rect_l, rect_w)
                intersection_square = rect.intersection_square(src_rect)
                variants.append((intersection_square, j))
        _, orientation = max(variants, key=itemgetter(0))
        if best and orientation == 1 and best.is_rotatable:
            best.rotate()

    return priority, orientation, best