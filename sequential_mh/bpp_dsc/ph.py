import sys
from collections import namedtuple

from .rectangle import PackedBlank

# PackedBlank = namedtuple('PackedBlank', ('blank', 'x', 'y'))
Tailing = namedtuple('Tailing', ('x', 'y', 'length', 'width'))


def ph_bpp(length, width, rectangles, x0=0., y0=0., first_priority=False):
    result = {}
    tailings = []
    max_priority= None

    if first_priority:
        priority_list = [p for p, group in rectangles.items() if group]
        if not priority_list:
            return {}, 0
        max_priority = min(priority_list)

    recursive_packing(
        x0, y0, length, width, rectangles, result, tailings,
        first_priority=max_priority
    )

    if result:
        total_l, total_w = [], []
        for _, list_r in result.items():
            total_l.append(max([r.y + r.rectangle.length for r in list_r]))
            total_w.append(max([r.x + r.rectangle.width for r in list_r]))
        total_l = max(total_l)
        total_w = max(total_w)
        s_1 = total_w * (length - total_l)
        s_2 = total_l * (width - total_w)
        if s_1 >= s_2:
            total_len = total_l
            total_width = width
        else:
            total_len = length
            total_width = total_w
    else:
        total_len, total_width = 0., 0.

    return result, total_len - y0, total_width - x0, tailings


def recursive_packing(x, y, length, width, rectangles, result, tailings,
                      first_priority=False):
    variant, best, priorities = [], [], []
    if first_priority:
        priorities.append(first_priority)
        v, b = get_best_fig(length, width, rectangles[first_priority])
        variant.append(v)
        best.append(b)
    else:
        for p, group in rectangles.items():
            priorities.append(p)
            v, b = get_best_fig(length, width, group)
            variant.append(v)
            best.append(b)

    for i, priority in enumerate(priorities):  # number_groups
        if variant[i] < 5:
            d, omega = best[i].size[:-1]
            if priority not in result:
                result[priority] = []
            result[priority].append(PackedBlank(best[i], x, y))
            rectangles[priority].remove(best[i])
            if variant[i] == 2:
                recursive_packing(
                    x, y + d, length - d, width, rectangles, result,
                    tailings, first_priority=first_priority
                )
            elif variant[i] == 3:
                recursive_packing(
                    x + omega, y, length, width - omega, rectangles, result,
                    tailings, first_priority=first_priority
                )
            elif variant[i] == 4:
                min_w = min_l = sys.maxsize
                for p, group in rectangles.items():
                    for blank in group:
                        min_l = min(min_l, blank.length)
                        min_w = min(min_w, blank.width)
                min_w = min(min_w, min_l)
                min_l = min_w
                if width - omega < min_w:
                    tailings.append(Tailing(omega, y, d, width - omega))
                    recursive_packing(
                        x, y + d, length - d, width, rectangles, result,
                        tailings, first_priority=first_priority
                    )
                elif length - d < min_l:
                    tailings.append(Tailing(x, y + d, length - d, omega))
                    recursive_packing(
                        x + omega, y, length, width - omega, rectangles, 
                        result, tailings, first_priority=first_priority
                    )
                elif omega < min_w:
                    recursive_packing(
                        x + omega, y, d, width - omega, rectangles, result,
                        tailings
                    )
                    recursive_packing(
                        x, y + d, length - d, width, rectangles, result,
                        tailings, first_priority=first_priority
                    )
                else:
                    recursive_packing(
                        x, y + d, length - d, omega, rectangles, result,
                        tailings
                    )
                    recursive_packing(
                        x + omega, y, length, width - omega, rectangles, 
                        result, tailings, first_priority=first_priority
                    )
            break


def get_best_fig(length, width, rectangles):
    priority, orientation, best = 6, None, None
    for rect in rectangles:
        size = rect.size[:-1]
        for j in range(1 + rect.is_rotatable):
            rect_l = size[(0 + j) % 2]
            rect_w = size[(1 + j) % 2]
            if priority > 1 and rect_l == length and rect_w == width:
                priority, orientation, best = 1, j, rect
            elif priority > 2 and rect_l < length and rect_w == width:
                priority, orientation, best = 2, j, rect
            elif priority > 3 and rect_l == length and rect_w < width:
                priority, orientation, best = 3, j, rect
            elif priority > 4 and rect_l < length and rect_w < width:
                priority, orientation, best = 4, j, rect
            elif priority > 5:
                priority, orientation, best = 5, j, rect
    if best and orientation != 0 and best.is_rotatable:
        best.rotate()
    return priority, best
