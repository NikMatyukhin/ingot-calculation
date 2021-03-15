"""Модуль протоколов и типов для аннотаций

:Date: 14.03.2020
:Version: 0.1
:Authors:
    - Воронов Владимир Сергеевич
"""

from typing import Protocol, Union


Number = Union[int, float]
Vec2 = tuple[Number, Number]
Vec3 = tuple[Number, Number, Number]


class SupportRotate(Protocol):
    """Протокол поддержки разворота"""
    def rotate(self) -> None:
        """Поворот на 90 градусов"""
        raise NotImplementedError

    @property
    def is_rotatable(self) -> bool:
        """Возможность поворота"""
        raise NotImplementedError


class RectangleProtocol(SupportRotate, Protocol):
    """Протокол прямоугольника"""
    length: Number
    width: Number

    @property
    def size(self) -> Vec3:
        """Размеры, три параметра"""
        raise NotImplementedError

    @property
    def area(self) -> Number:
        """Площадь фигуры"""
        raise NotImplementedError
