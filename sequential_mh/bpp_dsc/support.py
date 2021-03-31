"""Модуль вспомогательных функций"""


from collections import deque
from typing import Union


Number = Union[int, float]
Vec3 = tuple[Number, Number, Number]


def is_subrectangle(src: Vec3, dst: Vec3, with_rotate: bool=True) -> bool:
    """Проверка вложения прямугольника в другой прямоугольник.

    :param src: стороны прямоугольника который необходимо вписать
                в виде (длина, ширина, высота)
    :type src: tuple[Number, Number, Number]
    :param dst: стороны большого прямоугольника в виде (длина, ширинаб высота)
    :type dst: tuple[Number, Number, Number]
    :param with_rotate: флаг, разрешающий поворот вписываемого
                        прямоугольника на 90 градусов, по умолчанию True
    :type with_rotate: bool
    :return: True, если прямоугольник можно вписать
             и False в противном случае
    :rtype: bool
    """
    if dst[-1] == src[-1]:
        if with_rotate:
            return (
                max(src[:2]) <= max(dst[:2]) and min(src[:2]) <= min(dst[:2])
            )
        return src[0] <= dst[0] and src[1] <= dst[1]
    return False


def is_subrectangle_with_def(src: Vec3, dst: Vec3, rolldir: int,
                             with_rotate: bool=True, extension: Number=1):
    length, width, height = dst
    new_height = src[-1]
    if rolldir == 0:
        # по горизонтали
        width = deformation(width, height, new_height, extension)
    else:
        # по вертикали
        length = deformation(length, height, new_height, extension)
    return is_subrectangle(
        src, (length, width, new_height), with_rotate=with_rotate
    )


def deformation(length: Number, height: Number, new_height: Number,
                extension: Number=1) -> Number:
    if height == new_height:
        return length
    if height < new_height:
        extension = 1 / extension
    return (extension * length * height) / new_height


def dfs(root):
    """Обход дерева в глубину

    :param root: Корневой узел с которого начинается обход
    :type root: BaseNode или наследники
    :yield: Очередной узел дерева
    :rtype: BaseNode или наследники
    """
    stack = deque([root])
    while stack:
        node = stack.popleft()
        yield node
        stack.extendleft(reversed(node.list_of_children()))
