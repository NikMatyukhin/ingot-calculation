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
    delete_from_dict, dict_to_list, exclude_from_dict
)
from .rect import (
    Point, Rectangle, RectangleType, PackedRectangle,
    difference_rect, min_enclosing_rect
)
from .ph import ph_bpp, sort
from .visualize import visualize
from .est import Estimator
from ..bpp_dsc.rectangle import Direction


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


def rotate_all(rectangles, rolldir):
    for _, group in rectangles.items():
        for blank in group:
            if not blank.is_rotatable and blank.direction != rolldir:
                blank.rotate()
            elif blank.is_rotatable and blank.length > blank.width:
                blank.rotate()


def bpp_ts(length, width, height, g_height, rectangles, last_rolldir=None,
           first_priority=False,
           x_hem=(0, 0), y_hem=(0, 0), allowance=0, max_size=None,
           is_visualize=False):
    # rectangles - список прямоугольников
    # rectangles.sort()
    src_rect = Rectangle((0, 0), (width, length))
    min_rect = Rectangle((0, 0), (0, 0))
    if last_rolldir == Direction.H and max_size:
        max_size = max_size[::-1]
    sort(rectangles, sorting='width')
    if last_rolldir:
        rotate_all(rectangles, last_rolldir)
    main_region = Estimator(
        src_rect, height, g_height, limits=max_size,
        x_hem=x_hem, y_hem=y_hem
    )
    all_regions = [main_region]
    result, unplaced, all_tailings = [], [], []
    # rotate_all(rectangles)
    if first_priority:
        for_packing = rectangles[first_priority]
    else:
        for_packing = dict_to_list(rectangles)
        # for_packing = rectangles
    # while not is_empty_dict(for_packing):
    while for_packing:
        layout_options = []
        if not all_regions:
            unplaced.extend(dict_to_list(rectangles))
            break
        for _, region in enumerate(all_regions):
            tailings = []
            variant, _, best = get_best_fig(
                for_packing, region, main_region.rectangle, last_rolldir,
                (y_hem[0], x_hem[0]), allowance, *region.start
            )
            if best is None:
                continue
            if variant == 15:
                state = StateLayout([], [best], [], min_rect, 0, 0, 0)
                layout_options.append(state)
                continue

            dummy_hem = dummy_alw = None
            new_start = region.start
            # создание фиктивных прямоугольников под кромки и припуски
            if new_start.x == 0:
                if region.right_hem > 0:
                    # кромка справа и слева
                    if new_start.y == 0:
                        delta = region.bottom_hem
                    else:
                        delta = allowance
                    dummy_hem = Rectangle.create_by_size(
                        region.start, best.length + delta, region.left_hem
                    )
                    dummy_hem.rtype=RectangleType.EDGE
                    new_start = Point(region.left_hem, new_start.y)
                    tailings.append(dummy_hem)
                if allowance and new_start.y > 0:
                    # горизонтальный припуск
                    dummy_alw = Rectangle.create_by_size(
                        new_start, allowance, best.width
                    )
                    dummy_alw.rtype=RectangleType.ALLOWANCE
                    new_start = Point(region.left_hem, new_start.y + allowance)
                    tailings.append(dummy_alw)
            if new_start.y == 0:
                if region.bottom_hem > 0:
                    # кромка сверху и снизу
                    if region.start.x in (0, region.left_hem):
                        delta = 0
                    else:
                        delta = allowance
                    dummy_hem = Rectangle.create_by_size(
                        new_start, region.bottom_hem, best.width + delta
                    )
                    dummy_hem.rtype=RectangleType.EDGE
                    new_start = Point(new_start.x, region.bottom_hem)
                    tailings.append(dummy_hem)
                if allowance and new_start.x > region.left_hem:
                    # вертикальный припуск
                    dummy_alw = Rectangle.create_by_size(
                        new_start, best.length, allowance
                    )
                    dummy_alw.rtype=RectangleType.ALLOWANCE
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
                x, y = empty_rect.blp
                soft_type = 3
                if region.limits[1] + region.start.x == empty_rect.trp.x:
                    soft_type = 1
                elif region.limits[0] + region.start.y == empty_rect.trp.y:
                    soft_type = 2
                if x == 0:
                    soft_type = 1
                    if region.left_hem > 0:
                        # добавление правой кромки
                        dummy_hem = Rectangle.create_by_size(
                            empty_rect.blp, empty_rect.length + allowance, region.left_hem
                        )
                        dummy_hem.rtype=RectangleType.EDGE
                        usable_square += dummy_hem.square
                        empty_rect.blp = Point(region.left_hem, y)
                        tailings.append(dummy_hem)
                elif y == 0:
                    soft_type = 2
                    if region.left_hem > 0:
                        # добавление нижней кромки
                        dummy_hem = Rectangle.create_by_size(
                            empty_rect.blp, region.bottom_hem, empty_rect.width
                        )
                        dummy_hem.rtype=RectangleType.EDGE
                        usable_square += dummy_hem.square
                        empty_rect.blp = Point(empty_rect.blp.x, empty_rect.blp.y + region.bottom_hem)
                        tailings.append(dummy_hem)
                if allowance and x > 0:
                    # добавление вертикального припуска
                    dummy_alw = Rectangle.create_by_size(
                        empty_rect.blp, empty_rect.length, allowance
                    )
                    dummy_alw.rtype=RectangleType.ALLOWANCE
                    usable_square += dummy_alw.square
                    empty_rect.blp = Point(empty_rect.blp.x + allowance, empty_rect.blp.y)
                    tailings.append(dummy_alw)
                if allowance and y > 0:
                    # сразу добавляется горизонтальный припуск
                    dummy_alw = Rectangle.create_by_size(
                        empty_rect.blp, allowance, empty_rect.width
                    )
                    dummy_alw.rtype=RectangleType.ALLOWANCE
                    usable_square += dummy_alw.square
                    empty_rect.blp = Point(empty_rect.blp.x, empty_rect.blp.y + allowance)
                    tailings.append(dummy_alw)

                dist = main_region(*empty_rect.trp)
                if dist[0] == 0 or dist[1] == 0:
                    soft_type = 0
                _results = []
                variants = [0] if soft_type == 0 else [0, soft_type]
                for v in variants:
                    _usable_square = 0
                    res, *_, _tailings = ph_bpp(
                        empty_rect.length, empty_rect.width,
                        deepcopy(exclude_from_dict(best, rectangles)),
                        *empty_rect.blp, allowance, first_priority=False,
                        sorting='length', soft_type=v, k=0.8
                    )
                    placed_blanks = list(chain.from_iterable(res.values()))
                    if placed_blanks:
                        _mrect = min_enclosing_rect(
                            [Rectangle.create_by_size((r.x, r.y), r.rectangle.length, r.rectangle.width) for r in placed_blanks]
                        )
                        _mrect = min_enclosing_rect((_mrect, new_min_rect))
                    else:
                        _mrect = new_min_rect
                    if main_region(*_mrect.trp):
                        if placed_blanks:
                            _usable_square += sum(b.rectangle.area for b in placed_blanks)
                            _usable_square += sum(r.square for r in _tailings if r.rtype != RectangleType.RESIDUAL)
                        ef = (usable_square + _usable_square) / _mrect.square
                        if main_region(*_mrect.trp):
                            _results.append((ef, placed_blanks, _mrect, _tailings, _usable_square))
                _, res, _mrect, _tailings, _usable_square = max(_results, key=itemgetter(0))
                usable_square += _usable_square
                new_min_rect = _mrect
                tailings.extend(_tailings)
                blanks.extend(res)
            status = StateLayout(
                blanks, [], tailings, new_min_rect,
                usable_square / square,  intersection_square,
                new_min_rect.min_side / new_min_rect.max_side
            )
            layout_options.append(status)
        # выбрать вариант размещения
        # TODO: Может сравнивать как длины векторов???
        layout = max(
            enumerate(layout_options), key=lambda item: (item[1].efficiency,
                                              item[1].inters_square,
                                              item[1].aspect_ratio)
        )
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
        all_regions = main_region.cut(point=min_rect.trp)

        if first_priority:
            for_packing = rectangles[first_priority]
        else:
            for_packing = dict_to_list(rectangles)

        if is_visualize:
            l_max = length * height / g_height
            w_max = width * height / g_height
            visualize(main_region, result, all_tailings,
                      xlim=w_max, ylim=l_max)

    if min_rect.length > 0 and min_rect.width > 0:
        if x_hem[1] > 0:
            # правая кромка/торец
            dummy = Rectangle.create_by_size(min_rect.brp, min_rect.length, x_hem[1])
            all_tailings.append(dummy)
            min_rect = min_enclosing_rect((min_rect, dummy))
            main_region.update(min_rect, with_lim=False)
        if y_hem[1] > 0:
            # верхняя кромка/торец
            dummy = Rectangle.create_by_size(min_rect.tlp, y_hem[1], min_rect.width)
            all_tailings.append(dummy)
            min_rect = min_enclosing_rect((min_rect, dummy))
            main_region.update(min_rect, with_lim=False)

    if main_region.rectangle != src_rect:
        rect = min_enclosing_rect((main_region.rectangle, src_rect))
        if rect.length > 0 and rect.width > 0:
            main_region.update(rect, with_lim=False)
    return src_rect, main_region, min_rect, result, unplaced, all_tailings


def get_best_fig(rectangles, estimator, src_rect, last_rolldir,
                 hem, allowance=0, x0=0, y0=0):
    priority, orientation, best = 16, None, None
    w_0 = estimator.min_width_lim
    l_0 = estimator.min_length_lim
    w_max = estimator.max_width_lim
    if x0 == 0 and hem[1] > 0:
        # кромка справа и слева
        x0 += hem[1]
    if y0 == 0 and hem[0] > 0:
        # кромка сверху и снизу
        y0 += hem[0]
    # для припуска
    if x0 in (0, hem[1]):
        y0 += allowance
    elif y0 in (0, hem[0]):
        x0 += allowance
    for rect in rectangles:
        if last_rolldir is not None and not rect.is_rotatable:
            if rect.direction != last_rolldir:
                rect.rotate()
        size = rect.size[:-1]
        for j in range(1 + rect.is_rotatable):
            rect_w = size[(1 + j) % 2]
            rect_l = size[(0 + j) % 2]
            trp = estimator.rectangle.trp
            estimate_point = max(x0 + rect_w, trp.x), max(y0 + rect_l, trp.y)
            if estimator(*estimate_point) is None:
                continue
            dist = estimator(x0 + rect_w, y0)
            if dist is None:
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
            elif priority > 13 and w_0 < rect_w < w_max and rect_l < min(l_0, l_max):
                # вариант 13
                priority, orientation, best = 13, j, rect
            elif priority > 14 and rect_w < w_0 and rect_l < min(l_0, l_max):
                # вариант 14
                priority, orientation, best = 14, j, rect
            elif priority > 15:
                # ничего не входит
                priority, orientation, best = 15, j, rect
    if priority > 15:
        priority, orientation, best = 15, 0, rectangles[-1]
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
        if priority == 14:
            best_intersection, _ = max(variants, key=itemgetter(0))
            orientation_by_intersection = [v[1] for v in variants if v[0] == best_intersection]
            orientation_by_min_area = best_orientation(best, src_rect, x0, y0)
            if orientation_by_min_area not in orientation_by_intersection:
                orientation = orientation_by_intersection[0]
            else:
                orientation = orientation_by_min_area
        if best and orientation == 1 and best.is_rotatable:
            best.rotate()

    return priority, orientation, best


def best_orientation(rectangle, container, x, y):
    size = rectangle.size[:-1]
    variants = []
    for j in range(1 + rectangle.is_rotatable):
        rect_w = size[(1 + j) % 2]
        rect_l = size[(0 + j) % 2]
        area_1 = (x + rect_w) * container.length
        area_2 = (y + rect_l) * container.width
        variants.append((min(area_1, area_2), j))
    return min(variants, key=itemgetter(0))[1]
