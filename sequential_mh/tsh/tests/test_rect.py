"""Тесты для модуля tsh.rect"""

import pytest

from ..rect import Rectangle, Point, difference_rect, min_enclosing_rect


@pytest.mark.parametrize(
    'point1, point2',
    [
        [(1, 2), (4, 5)],
        [(6, 7), (1, 3)],
    ]
)
def test_create_rect(point1, point2):
    """Создание прямоугольника"""
    rect = Rectangle(point1, point2)
    assert rect.blp == Point(*min(point1, point2))
    assert rect.trp == Point(*max(point1, point2))


@pytest.mark.parametrize(
    'point1, point2, expected',
    [
        [(1, 2), (4, 5), 3],
        [(6, 7), (1, 3), 4],
    ]
)
def test_length(point1, point2, expected):
    """Тест на длину прямоугольника"""
    rect = Rectangle(point1, point2)
    assert rect.length == expected


@pytest.mark.parametrize(
    'point1, point2, expected',
    [
        [(1, 2), (4, 5), 3],
        [(6, 7), (1, 3), 5],
    ]
)
def test_width(point1, point2, expected):
    """Тест на ширину прямоугольника"""
    rect = Rectangle(point1, point2)
    assert rect.width == expected


@pytest.mark.parametrize(
    'rect1, rect2, expected',
    [
        [[(1, 2), (4, 5)], [(1, 2), (4, 5)], []],
        [[(1, 2), (4, 5)], [(1, 2), (3, 4)], [(3, 4)]],
        [[(1, 2), (5, 6)], [(2, 3), (4, 5)], [(2, 3), (4, 3), (4, 5), (2, 5)]],
    ]
)
def test_inside_point(rect1, rect2, expected):
    """Тест на принадлежность точки прямоугольнику"""
    rect_1 = Rectangle(*rect1)
    rect_2 = Rectangle(*rect2)
    result = rect_1.inside_points(rect_2)
    assert result == list(map(lambda x: Point(*x), expected))


@pytest.mark.parametrize(
    'rect1, rect2, expected',
    [
        [[(1, 2), (4, 5)], [(1, 2), (4, 5)], []],
        [[(1, 2), (5, 6)], [(2, 3), (4, 5)], []],
        [[(1, 2), (4, 5)], [(1, 2), (3, 4)], [(3, 2), (1, 4)]],
        [[(1, 2), (4, 5)], [(3, 4), (4, 5)], [(4, 4), (3, 5)]],
        [[(1, 2), (4, 5)], [(1, 3), (3, 5)], [(1, 3), (3, 5)]],
        [[(1, 2), (4, 5)], [(2, 2), (4, 4)], [(2, 2), (4, 4)]],
    ]
)
def test_boundary_points(rect1, rect2, expected):
    """Тест на принадлежность точки границам прямоугольника"""
    rect_1 = Rectangle(*rect1)
    rect_2 = Rectangle(*rect2)
    result = rect_1.boundary_points(rect_2)
    assert result == list(map(lambda x: Point(*x), expected))


@pytest.mark.parametrize(
    'dst, rect1, rect2, expected',
    [
        [[(0, 0), (6, 10)], [(0, 8), (2, 10)], [(0, 0), (6, 8)], [(2, 8), (6, 10)]],
        [[(0, 0), (10, 5)], [(0, 0), (7, 5)], [(7, 0), (10, 3)], [(7, 3), (10, 5)]],
        [[(0, 0), (10, 9)], [(0, 0), (8, 6)], [(8, 0), (10, 9)], [(0, 6), (8, 9)]],
        [[(0, 0), (8, 7)], [(0, 0), (6, 6)], [(0, 6), (8, 7)], [(6, 0), (8, 6)]],
    ]
)
def test_difference_rect(dst, rect1, rect2, expected):
    """Тест на разность перекрывающихся прямоугольников"""
    rect_1 = Rectangle(*rect1)
    rect_2 = Rectangle(*rect2)
    rect_3 = Rectangle(*dst)
    result = difference_rect(rect_3, [rect_1, rect_2])
    assert len(result) == 1
    result = result[0]
    assert result.blp.x == expected[0][0] and result.blp.y == expected[0][1]
    assert result.trp.x == expected[1][0] and result.trp.y == expected[1][1]


@pytest.mark.parametrize(
    'dst, rect1, rect2',
    [
        [[(0, 0), (6, 10)], [(0, 7), (6, 10)], [(0, 0), (6, 7)]],
        [[(0, 0), (10, 6)], [(7, 0), (10, 6)], [(0, 0), (7, 6)]],
    ]
)
def test_difference_rect_empty(dst, rect1, rect2):
    """Тест на разность не перекрывающихся прямоугольников"""
    rect_1 = Rectangle(*rect1)
    rect_2 = Rectangle(*rect2)
    rect_3 = Rectangle(*dst)
    res = difference_rect(rect_3, [rect_1, rect_2])
    assert len(res) == 0


@pytest.mark.parametrize(
    'rect1, rect2, expected',
    [
        [[(0, 8), (2, 10)], [(0, 0), (6, 8)], ((0, 0), (6, 10))],
        [[(0, 0), (7, 5)], [(7, 0), (10, 3)], ((0, 0), (10, 5))],
        [[(0, 0), (8, 6)], [(8, 0), (10, 9)], ((0, 0), (10, 9))],
        [[(0, 0), (6, 6)], [(0, 6), (8, 7)], ((0, 0), (8, 7))],
        [[(0, 7), (6, 10)], [(0, 0), (6, 7)], ((0, 0), (6, 10))],
        [[(7, 0), (10, 6)], [(0, 0), (7, 6)], ((0, 0), (10, 6))],
    ]
)
def test_min_enclosing_rect(rect1, rect2, expected):
    """Тест на минимальный объемлющий прямоугольник"""
    rect_1 = Rectangle(*rect1)
    rect_2 = Rectangle(*rect2)
    result = min_enclosing_rect((rect_1, rect_2))
    assert result.blp == Point(*expected[0])
    assert result.trp == Point(*expected[1])
