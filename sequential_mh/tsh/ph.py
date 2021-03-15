"""Модифицированный алгоритм приоритетной эвристики.

Алгоритм предназначен для решения задачи упаковки (BPP).
Оригинальный алгоритм описан в статье:
Zhang, D., Shi, L., Leung, S.C.H., Wu, T.: A priority heuristic for the
guillotine rectangular packing problem. Information Processing Letters.
116, 15–21 (2016). https://doi.org/10.1016/j.ipl.2015.08.008

Ссылка на работу:
https://www.sciencedirect.com/science/article/pii/S0020019015001519?via%3Dihub

Модификация заключается в добавлении возможности работы с приоритетами,
показывающими важность изготовления прямоугольника.
"""

from operator import attrgetter
import sys

from .rect import Rectangle, PackedRectangle


def rotate_all(rectangles):
    for _, group in rectangles.items():
        for blank in group:
            if blank.length > blank.width and blank.is_rotatable:
                blank.rotate()


def sort(rectangles, sorting: str='width'):
    """Сортировка прямоугольников

    Сортировка осуществляется "на месте".
    Возможны варианты сортировки:
    - по ширине (sorting='width'), по умолчанию
    - по длине (sorting='length')

    :param rectangles: набор прямоугольников в виде словаря,
                       где ключи - приоритеты, а значения списки
                       прямоугольников
    :type rectangles: dict[int, Iterable[RectangleProtocol]]
    :param sorting: параметр, задающий вариант сортировки, возможны два
                    варианта: 'width', 'length', defaults to 'width'
    :type sorting: str, optional
    :raises ValueError: В случае, если аргумент sorting имеет значение,
                        отличное от указанных, вызывается исключение.
    """
    if sorting not in ('width', 'length'):
        raise ValueError('The algorithm only supports sorting by width '
                            f'or length but {sorting} was given.')

    for _, group in rectangles.items():
        for blank in group:
            if blank.length > blank.width:
                blank.rotate()
        group.sort(key=attrgetter(sorting), reverse=True)


def ph_bpp(length, width, rectangles, x0=0., y0=0., first_priority=False,
           sorting='width'):
    """Алгоритм приоритетной эвристики

    :param length: длина контейнера
    :type length: int или float
    :param width: ширина контейнера
    :type width: int или float
    :param rectangles: набор прямоугольников, сгруппированных по приоритетам
    :type rectangles: dict[int, Iterable[RectangleProtocol]]
    :param x0: начальная координата по оси X, defaults to 0.
    :type x0: int или float, optional
    :param y0: начальная координата по оси Y, defaults to 0.
    :type y0: int или float, optional
    :param first_priority: флаг учета приоритетности, defaults to False
    :type first_priority: bool, optional
    :param sorting: параметр, задающий вариант сортировки, возможны два
                    варианта: 'width', 'length', defaults to 'width'
    :type sorting: str, optional
    :return: набор размещенных прямоугольников, в том же формате, что и
             входной набор, используемая длина, используемая ширина и
             набор неиспользуемых частей
    :rtype: tuple[dict[int, Iterable[PackedRectangle]],
                  Union[int, float], Union[int, float], list[Rectangle]]
    """
    result = {}
    tailings = []
    max_priority= None

    if first_priority:
        priority_list = [p for p, group in rectangles.items() if group]
        if not priority_list:
            return {}, 0
        max_priority = min(priority_list)

    sort(rectangles, sorting=sorting)

    recursive_packing(
        x0, y0, length, width, rectangles, result, tailings,
        first_priority=max_priority
    )

    if result:
        total_l, total_w = [], []
        for _, list_r in result.items():
            # total_l.append(max([r.y + r.blank.length for r in list_r]))
            # total_w.append(max([r.x + r.blank.width for r in list_r]))
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
    """Рекурсивная процедура упаковки

    :param x: стартовая координата по оси X
    :type x: int или float
    :param y: стартовая координата по оси Y
    :type y: int или float
    :param length: длина контейнера
    :type length: int или float
    :param width: ширина контейнера
    :type width: int или float
    :param rectangles: набор прямоугольников
    :type rectangles: dict[int, Iterable[RectangleProtocol]]
    :param result: набор размещенных прямоугольников
    :type result: dict[int, Iterable[PackedRectangle]]
    :param tailings: список неиспользуемых частей
    :type tailings: list[Rectangle]
    :param first_priority: флаг учета приоритетов, defaults to False
    :type first_priority: bool, optional
    """
    best_rect = []
    if first_priority:
        v, b = get_best_fig(length, width, rectangles[first_priority])
        best_rect.append((b, first_priority, v))
    else:
        for p, group in rectangles.items():
            v, b = get_best_fig(length, width, group)
            best_rect.append((b, p, v))

    best_rect.sort(key=lambda x: (x[2], x[1]))

    for best, p, variant in best_rect:
        if variant >= 5:
            tailings.append(Rectangle.create_by_size((x, y), length, width))
        else:  # if variant < 5
            # omega, d = best.size[:-1]
            d, omega = best.size[:-1]
            if p not in result:
                result[p] = []
            result[p].append(PackedRectangle(best, x, y))
            rectangles[p].remove(best)
            if variant == 2:
                recursive_packing(
                    x, y + d, length - d, width, rectangles, result,
                    tailings, first_priority=first_priority
                )
            elif variant == 3:
                recursive_packing(
                    x + omega, y, length, width - omega, rectangles, result,
                    tailings, first_priority=first_priority
                )
            elif variant == 4:
                min_w = min_l = sys.maxsize
                for _, group in rectangles.items():
                    for blank in group:
                        min_l = min(min_l, blank.length)
                        min_w = min(min_w, blank.width)
                min_w = min(min_w, min_l)
                min_l = min_w
                if width - omega < min_w:
                    tailings.append(Rectangle.create_by_size(
                        (x + omega, y), d, width - omega
                    ))
                    recursive_packing(
                        x, y + d, length - d, width, rectangles, result,
                        tailings, first_priority=first_priority
                    )
                elif length - d < min_l:
                    tailings.append(Rectangle.create_by_size(
                        (x, y + d), length - d, omega
                    ))
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
    """Выбор лучшей фигуры для упаковки

    Выбор осуществляется на основе "внутренних" приоритетов от 1 до 5.
    Они характеризуют варианты размещения прямоугольников.
    Так 1 означает, что прямоугольник занимает всю доступную площадь,
    а 5 - прямоугольник невозможно разместить.

    :param length: доступная для размещения длина контейнера
    :type length: int или float
    :param width: доступная для размещения ширина контейнера
    :type width: int или float
    :param rectangles: набор прямоугольников
    :type rectangles: Iterable[RectangleProtocol]
    :return: кортеж из внутреннего приоритета прямоугольника и самого
             прямоугольника.
    :rtype: tuple[int, RectangleProtocol]
    """
    priority, orientation, best = 6, None, None
    for rect in rectangles:
        size = rect.size[:-1]
        for j in range(1 + rect.is_rotatable):
            rect_w = size[(1 + j) % 2]
            rect_l = size[(0 + j) % 2]
            if priority > 1 and rect_l == length and rect_w == width:
                priority, orientation, best = 1, j, rect
            # elif priority > 2 and rect_l == length and rect_w < width:
            #     priority, orientation, best = 2, j, rect
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
