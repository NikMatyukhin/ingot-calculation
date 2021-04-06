"""Модуль тестирования класса заготовок

:Date: 06.04.2021
:Version: 0.1
:Authors:
    - Воронов Владимир Сергеевич
"""

import math
import pytest

from ..rectangle import Blank, Material, Direction


def test_size():
    """Тест размеров"""
    blank = Blank(100, 200, 3, 1)
    assert blank.size == (100, 200, 3)


@pytest.mark.parametrize(
    'size, expected',
    [
        [size:=(100, 200), math.prod(size)],
        [(0, 200), 0],
        [(50, 0), 0],
    ]
)
def test_area(size: tuple[int, int], expected):
    """Тест площади"""
    blank = Blank(*size, 3, 1)
    assert blank.area == expected


@pytest.mark.parametrize(
    'size, expected',
    [
        [size:=(100, 200, 3), math.prod(size)],
        [(0, 200, 3), 0],
        [(100, 0, 3), 0],
        [(100, 200, 0), 0],
    ]
)
def test_volume(size: tuple[int, int, int], expected):
    """Тест объема"""
    blank = Blank(*size, 1)
    assert blank.volume == expected


@pytest.mark.parametrize(
    'size, material, expected',
    [
        [size:=(100, 200, 3), Material('qwe', 2, 1), math.prod(size) * 2],
        [size:=(100, 200, 3), Material('qwe', 1, 1), math.prod(size)],
        [(100, 200, 3), Material('qwe', 0, 1), 0],
        [(100, 200, 3), None, 0],
        [(0, 200, 3), Material('qwe', 2, 1), 0],
        [(100, 0, 3), Material('qwe', 2, 1), 0],
        [(100, 200, 0), Material('qwe', 2, 1), 0],
    ]
)
def test_mass(size: tuple[int, int, int], material, expected):
    """Тест массы"""
    blank = Blank(*size, 1, material=material)
    assert blank.mass == expected


@pytest.mark.parametrize(
    'size, direction, expected',
    [
        [(100, 200), None, Direction.A],
        [(100, 200), Direction.A, Direction.A],
        [(100, 200), Direction.P, Direction.V],
        [(300, 100), Direction.P, Direction.H],
    ]
)
def test_direction(size: tuple[int, int], direction, expected):
    """Тест направления"""
    blank = Blank(*size, 2, 1, direction=direction)
    assert blank.direction == expected


@pytest.mark.parametrize(
    'direction, expected',
    [
        [None, True],
        [Direction.A, True],
        [Direction.P, False],
    ]
)
def test_is_rotatable(direction, expected):
    blank = Blank(100, 50, 2, 1, direction=direction)
    assert blank.is_rotatable == expected


@pytest.mark.parametrize(
    'blank_b, expected',
    [
        [Blank(100, 50, 2, 1), True],
        [Blank(100, 50, 3, 1), False],
        [Blank(100, 50, 2, 2), False],
        [Blank(100, 55, 2, 1), False],
        [Blank(50, 100, 2, 1), True],
        [Blank(50, 100, 4, 1), False],
        [Blank(50, 102, 2, 1), False],
    ]
)
def test_eq_without_direction(blank_b, expected):
    blank_a = Blank(100, 50, 2, 1)
    assert (blank_a == blank_b) is expected


@pytest.mark.parametrize(
    'blank_b, expected',
    [
        [Blank(100, 50, 2, 1, Direction.A), True],
        [Blank(100, 50, 3, 1, Direction.A), False],
        [Blank(100, 50, 2, 2, Direction.A), False],
        [Blank(100, 55, 2, 1, Direction.A), False],
        [Blank(50, 100, 2, 1, Direction.A), True],
        [Blank(50, 100, 4, 1, Direction.A), False],
        [Blank(50, 105, 2, 1, Direction.A), False],
    ]
)
def test_eq_direction_a(blank_b, expected):
    blank_a = Blank(100, 50, 2, 1, direction=Direction.A)
    assert (blank_a == blank_b) is expected


@pytest.mark.parametrize(
    'blank_b, expected',
    [
        [Blank(100, 50, 2, 1, Direction.P), True],
        [Blank(100, 50, 3, 1, Direction.P), False],
        [Blank(100, 50, 2, 2, Direction.P), False],
        [Blank(100, 55, 2, 1, Direction.P), False],
        [Blank(50, 100, 2, 1, Direction.P), True],
        [Blank(50, 100, 4, 1, Direction.P), False],
        [Blank(50, 105, 2, 1, Direction.P), False],
        [Blank(100, 55, 2, 1, Direction.P), False],
    ]
)
def test_eq_direction_p(blank_b, expected):
    blank_a = Blank(100, 50, 2, 1, direction=Direction.P)
    assert (blank_a == blank_b) is expected


@pytest.mark.parametrize(
    'size, direction, expected',
    [
        [(100, 50), None, Direction.A],
        [(100, 50), Direction.A, Direction.A],
        [(100, 50), Direction.P, Direction.V],
        [(50, 100), Direction.P, Direction.H],
    ]
)
def test_rotate(size: tuple[int, int], direction, expected):
    """Тест поворота"""
    blank = Blank(*size, 2, 1, direction=direction)
    assert blank.size == (*size, 2)
    # assert blank.direction == direction
    blank.rotate()
    assert blank.size == (*size[::-1], 2)
    assert blank.direction == expected
