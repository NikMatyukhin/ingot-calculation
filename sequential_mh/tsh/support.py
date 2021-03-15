"""Вспомогательные функции"""


from itertools import chain, groupby
from operator import attrgetter


def is_empty_dict(some_dict) -> bool:
    """Проверка словаря на пустоту"""
    return not any(bool(l) for _, l in some_dict.items())


def dict_to_list(some_dict, attr='priority'):
    """Преобразование словаря в список"""
    if attr:
        kwargs = {'key': attrgetter(attr)}
    else:
        kwargs = {}
    return sorted(chain.from_iterable(some_dict.values()), **kwargs)


def exclude_from_dict(src, dst_dict, attr='priority'):
    """Удаление объекта из словаря с созданием нового словаря"""
    new_dict = {}
    if isinstance(src, (list, tuple)):
        src_list = sorted(src, key=attrgetter(attr))
        groups = groupby(src_list, key=attrgetter(attr))
    else:
        groups = groupby([src], key=attrgetter(attr))
    groups = {k: list(v) for k, v in groups}

    for key, values in dst_dict.items():
        new_dict[key] = values.copy()
        if key in groups:
            for item in groups[key]:
                new_dict[key].remove(item)
    return new_dict


def delete_from_dict(src, dst_dict, attr='priority'):
    """Удаление объекта из словаря 'на месте'"""
    if isinstance(src, list):
        src = sorted(src, key=attrgetter(attr))
        src = {k: list(v) for k, v in groupby(src, key=attrgetter(attr))}
    for key, values in src.items():
        if key in dst_dict:
            for item in values:
                dst_dict[key].remove(item)


def group_by_priority(rectangles):
    """Группировка прямоугольников по приоритету"""
    res = {}
    for rect in rectangles:
        if rect.p in res:
            res[rect.p].append(rect)
        else:
            res[rect.p] = [rect]
    return res
