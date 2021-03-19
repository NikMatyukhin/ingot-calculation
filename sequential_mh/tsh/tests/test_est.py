"""Модуль тестирования оценщика размеров

:Date: 12.03.2021
:Version: 0.1
:Authors:
    - Воронов Владимир Сергеевич
"""

import pytest

from ..rect import Rectangle, Point
from ..est import Estimator


@pytest.mark.parametrize(
    'rect, start, res',
    [
        [Rectangle((0, 0), (7, 5)), (0, 0), 7.5],
        [Rectangle((0, 0), (7, 5)), None, 7.5],
        [Rectangle((0, 0), (7, 5)), (1, 1), 6.5],
        [Rectangle((0, 0), (7, 5)), (0, 7.5), 0],
    ]
)
def test_max_length(rect, start, res):
    """Тест максимальной длины без ограничений"""
    height = 3
    g_height = 2
    est = Estimator(rect, height, g_height, start=start)
    assert est.max_length == res
    if start is None:
        assert est.start == Point(0, 0)


@pytest.mark.parametrize(
    'rect, start, res',
    [
        [Rectangle((0, 0), (7, 5)), (0, 0), 5],
        [Rectangle((0, 0), (7, 5)), None, 5],
        [Rectangle((0, 0), (7, 5)), (1, 1), 4],
    ]
)
def test_min_length(rect, start, res):
    """Тест минимальной длины без ограничений"""
    height = 3
    g_height = 2
    est = Estimator(rect, height, g_height, start=start)
    assert est.min_length == res


@pytest.mark.parametrize(
    'rect, start, res',
    [
        [Rectangle((0, 0), (7, 5)), (0, 0), 10.5],
        [Rectangle((0, 0), (7, 5)), None, 10.5],
        [Rectangle((0, 0), (7, 5)), (1, 1), 9.5],
        [Rectangle((0, 0), (7, 5)), (10.5, 0), 0],
    ]
)
def test_max_width(rect, start, res):
    """Тест максимальной ширины без ограничений"""
    height = 3
    g_height = 2
    est = Estimator(rect, height, g_height, start=start)
    assert est.max_width == res


@pytest.mark.parametrize(
    'rect, start, res',
    [
        [Rectangle((0, 0), (7, 5)), (0, 0), 7],
        [Rectangle((0, 0), (7, 5)), None, 7],
        [Rectangle((0, 0), (7, 5)), (1, 1), 6],
    ]
)
def test_min_width(rect, start, res):
    """Тест минимальной ширины без ограничений"""
    height = 3
    g_height = 2
    est = Estimator(rect, height, g_height, start=start)
    assert est.min_width == res


@pytest.mark.parametrize(
    'rect, start, res',
    [
        [Rectangle((0, 0), (7, 5)), (0, 0), (7, 7.5)],
        [Rectangle((0, 0), (7, 5)), None, (7, 7.5)],
        [Rectangle((0, 0), (7, 5)), (1, 1), (7, 7.5)],
        [Rectangle((1, 1), (7, 5)), None, (7, 7)],
    ]
)
def test_tlp(rect, start, res):
    """Тест верхней левой точки без ограничений"""
    height = 3
    g_height = 2
    est = Estimator(rect, height, g_height, start=start)
    assert est.tlp == Point(*res)


@pytest.mark.parametrize(
    'rect, start, res',
    [
        [Rectangle((0, 0), (7, 5)), (0, 0), (10.5, 5)],
        [Rectangle((0, 0), (7, 5)), None, (10.5, 5)],
        [Rectangle((0, 0), (7, 5)), (1, 1), (10.5, 5)],
        [Rectangle((1, 1), (7, 5)), None, (10, 5)],
    ]
)
def test_trp(rect, start, res):
    """Тест верхней правой точки без ограничений"""
    height = 3
    g_height = 2
    est = Estimator(rect, height, g_height, start=start)
    assert est.trp == Point(*res)


@pytest.mark.parametrize(
    'rect, limits, res',
    [
        [Rectangle((0, 0), (7, 5)), None, 10.5],
        [Rectangle((0, 0), (7, 5)), (0, 0), 10.5],
        [Rectangle((0, 0), (7, 5)), (5, 8), 8],
    ]
)
def test_w_lim(rect, limits, res):
    """Тест свойства ограничения по ширине"""
    est = Estimator(rect, 3, 2, limits=limits)
    assert est.w_lim == res


@pytest.mark.parametrize(
    'rect, limits, res',
    [
        [Rectangle((0, 0), (7, 5)), None, 7.5],
        [Rectangle((0, 0), (7, 5)), (0, 0), 7.5],
        [Rectangle((0, 0), (7, 5)), (5, 8), 5],
    ]
)
def test_l_lim(rect, limits, res):
    """Тест свойства ограничения по длине"""
    est = Estimator(rect, 3, 2, limits=limits)
    assert est.l_lim == res


@pytest.mark.parametrize(
    'rect, point, res',
    [
        [Rectangle((0, 0), (7, 5)), (0, 0), (10.5, 7.5)],
        [Rectangle((0, 0), (7, 5)), (2, 1), (8.5, 6.5)],
        [Rectangle((0, 0), (7, 5)), (7, 5), (3.5, 2.5)],
        [Rectangle((0, 0), (7, 5)), (7, 1), (3.5, 6.5)],
        [Rectangle((0, 0), (7, 5)), (2, 5), (8.5, 2.5)],
    ]
)
def test_estimation_inside_small_rect(rect, point, res):
    """Проверка оценки при наличии точки внутри исходного прямоугольника"""
    est = Estimator(rect, 3, 2)
    assert est(*point) == res


@pytest.mark.parametrize(
    'rect, point, res',
    [
        [Rectangle((0, 0), (7, 5)), (6, 6), (2.75, 1.5)],
        [Rectangle((0, 0), (7, 5)), (0, 6), (8.75, 1.5)],
        [Rectangle((0, 0), (7, 5)), (7, 6), (1.75, 1.5)],
        [Rectangle((0, 0), (7, 5)), (0, 7.5), (7, 0)],
        [Rectangle((0, 0), (7, 5)), (7, 7.5), (0, 0)],
        [Rectangle((0, 0), (7, 5)), (6, 7.5), (1, 0)],
    ]
)
def test_estimation_at_the_top(rect, point, res):
    """Проверка оценки при наличии точки в верхней части области"""
    est = Estimator(rect, 3, 2)
    assert est(*point) == res


@pytest.mark.parametrize(
    'rect, point, res',
    [
        [Rectangle((0, 0), (7, 5)), (8, 4), (2.5, 2.5625)],
        [Rectangle((0, 0), (7, 5)), (8, 0), (2.5, 6.5625)],
        [Rectangle((0, 0), (7, 5)), (8, 5), (2.5, 1.5625)],
        [Rectangle((0, 0), (7, 5)), (10.5, 0), (0, 5)],
        [Rectangle((0, 0), (7, 5)), (10.5, 3), (0, 2)],
        [Rectangle((0, 0), (7, 5)), (10.5, 5), (0, 0)],
    ]
)
def test_estimation_on_the_right_side(rect, point, res):
    """Проверка оценки при наличии точки в правой части области"""
    est = Estimator(rect, 3, 2)
    assert est(*point) == res


@pytest.mark.parametrize(
    'rect, point, res',
    [
        [Rectangle((0, 0), (7, 5)), (8, 6), (0.75, 0.5625)],
        [Rectangle((0, 0), (7, 5)), (8.75, 6), (0, 0)],
        [Rectangle((0, 0), (7, 5)), (8, 6.5625), (0, 0)],
    ]
)
def test_estimation_in_the_corner(rect, point, res):
    """Проверка оценки при наличии точки в угловой части (кривая)"""
    est = Estimator(rect, 3, 2)
    assert est(*point) == res


@pytest.mark.parametrize(
    'rect, point',
    [
        [Rectangle((0, 0), (7, 5)), (0, 10)],
        [Rectangle((0, 0), (7, 5)), (7, 10)],
        [Rectangle((0, 0), (7, 5)), (15, 15)],
        [Rectangle((0, 0), (7, 5)), (15, 0)],
        [Rectangle((0, 0), (7, 5)), (15, 5)],
        [Rectangle((0, 0), (7, 5)), (8.5, 6.5)],
    ]
)
def test_estimation_outside(rect, point):
    """Проверка оценки при наличии точки вне области"""
    est = Estimator(rect, 3, 2)
    assert est(*point) is None


@pytest.mark.parametrize(
    'rect, limit, start, point, res',
    [
        [Rectangle((0, 0), (7, 5)), (0, 15), None, (1, 1), (9.5, 6.5)],
        [Rectangle((0, 0), (7, 5)), (0, 15), (1, 1), (2, 2), (8.5, 5.5)],
        [Rectangle((0, 0), (7, 5)), (0, 7), None, (1, 1), (6, 6.5)],
        [Rectangle((0, 0), (7, 5)), (0, 6), (1, 1), (2, 2), (5, 5.5)],
        [Rectangle((0, 0), (7, 5)), (0, 8), None, (1, 7), (6.5, 0.5)],
        [Rectangle((0, 0), (7, 5)), (0, 8), None, (1, 6), (7, 1.5)],
    ]
)
def test_estimation_with_w_lim(rect, limit, start, point, res):
    """Проверка оценки при ограничении ширины"""
    est = Estimator(rect, 3, 2, limits=limit, start=start)
    assert est(*point) == res


@pytest.mark.parametrize(
    'rect, limit, start, point, res',
    [
        [Rectangle((0, 0), (7, 5)), (15, 0), None, (1, 1), (9.5, 6.5)],
        [Rectangle((0, 0), (7, 5)), (15, 0), (1, 1), (2, 2), (8.5, 5.5)],
        [Rectangle((0, 0), (7, 5)), (7, 0), None, (1, 1), (9.5, 6)],
        [Rectangle((0, 0), (7, 5)), (6, 0), (1, 1), (2, 2), (8.5, 5)],
        [Rectangle((0, 0), (7, 5)), (6, 0), None, (10, 1), (0.5, 4.25)],
        [Rectangle((0, 0), (7, 5)), (6, 0), None, (8, 1), (2.5, 5)],
    ]
)
def test_estimation_with_l_lim(rect, limit, start, point, res):
    """Проверка оценки при наличии ограничений на длину"""
    est = Estimator(rect, 3, 2, limits=limit, start=start)
    assert est(*point) == res


@pytest.mark.parametrize(
    'rect, limit, start, point, res',
    [
        [Rectangle((0, 0), (7, 5)), (15, 15), None, (1, 1), (9.5, 6.5)],
        [Rectangle((0, 0), (7, 5)), (5, 6), (1, 1), (2, 2), (5, 4)],
        [Rectangle((0, 0), (7, 5)), (7, 9), None, (8, 6), (0.75, 0.5625)],
        [Rectangle((0, 0), (7, 5)), (7, 9), None, (2, 7), (5.5, 0)],
    ]
)
def test_estimation_with_lim(rect, limit, start, point, res):
    """Проверка оценки при наличии ограничений на длину и ширину"""
    est = Estimator(rect, 3, 2, limits=limit, start=start)
    assert est(*point) == res


@pytest.mark.parametrize(
    'rect, limit, start, point',
    [
        [Rectangle((0, 0), (7, 5)), (6, 8), None, (8, 7)],
        [Rectangle((0, 0), (7, 5)), (5, 5), (1, 1), (7, 7)],
    ]
)
def test_estimation_with_lim_fail(rect, limit, start, point):
    """Проверка оценки при наличии ограничений (неуспешной)"""
    est = Estimator(rect, 3, 2, limits=limit, start=start)
    assert est(*point) is None


@pytest.mark.parametrize(
    'rect, limit, start, hem, point, res',
    [
        [Rectangle((0, 0), (7, 5)), None, None, (1, 0), (1, 1), (7.75, 5.5)],
        [Rectangle((0, 0), (7, 5)), (7, 9), None, (1, 0), (1, 1), (7.75, 5.5)],
        [Rectangle((0, 0), (7, 5)), (7, 9), (1, 1), (1, 0), (2, 2), (6.75, 4.5)],
        [Rectangle((0, 0), (7, 5)), None, (1, 1), (1, 0), (2, 2), (6.75, 4.5)],
        [Rectangle((0, 0), (7, 5)), None, (1, 1), (1, 1), (2, 2), (6.75, 4.5)],
        [Rectangle((0, 0), (7, 5)), None, (1, 1), (0, 1), (2, 2), (7.5, 4.5625)],
    ]
)
def test_estimation_with_hem(rect, limit, start, hem, point, res):
    """Проверка оценки при наличии ограничений и кромки"""
    x_hem = hem[1], hem[1]
    y_hem = hem[0], hem[0]
    est = Estimator(
        rect, 3, 2, limits=limit, start=start, x_hem=x_hem, y_hem=y_hem
    )
    assert est(*point) == res


@pytest.mark.parametrize(
    'main_rect, rect, trp, height',
    [
        [Rectangle((0, 0), (7, 5)), Rectangle((0, 0), (7, 7.5)), (7, 7.5), 2],
        [Rectangle((0, 0), (7, 5)), Rectangle((0, 0), (10.5, 5)), (10.5, 5), 2],
        [Rectangle((0, 0), (7, 5)), Rectangle((0, 0), (8, 6.5625)), (8, 6.5625), 2],
        [Rectangle((0, 0), (7, 5)), Rectangle((0, 0), (5, 6.5)), (7, 6.5), 2.3076923076923075],
        [Rectangle((0, 0), (7, 5)), Rectangle((0, 0), (8, 6)), (8, 6), 2.1875],
        [Rectangle((0, 0), (7, 5)), Rectangle((0, 0), (5, 5)), (7, 5), 3],
    ]
)
def test_update(main_rect, rect, trp, height):
    """Тесты метода обновления области"""
    est = Estimator(main_rect, 3, 2)
    est.update(rect)
    assert est.rectangle.trp == Point(*trp)
    assert est.height == height


@pytest.mark.parametrize(
    'main_rect, rect',
    [
        [Rectangle((0, 0), (7, 5)), Rectangle((0, 0), (7, 8))],
        [Rectangle((0, 0), (7, 5)), Rectangle((0, 0), (11, 5))],
        [Rectangle((0, 0), (7, 5)), Rectangle((0, 0), (8, 7))],
        [Rectangle((0, 0), (7, 5)), Rectangle((0, 0), (15, 15))],
    ]
)
def test_update_exception(main_rect, rect):
    """Тесты метода обновления области (исключения)"""
    est = Estimator(main_rect, 3, 2)
    with pytest.raises(ValueError):
        est.update(rect)


def test_cut_0():
    """Тест на разрез прямоугольника, без результата"""
    rect = Rectangle((0, 0), (7, 5))
    est = Estimator(rect, 2, 2)
    assert est.cut() == []


@pytest.mark.parametrize(
    'rect, limit, start',
    [
        [Rectangle((0, 0), (7, 5)), (0, 7), (0, 5)],
        [Rectangle((0, 0), (7, 5)), (5, 0), (7, 0)],
    ]
)
def test_cut_1(rect, limit, start):
    """Тест на разрез прямоугольника, тот же прямоугольник"""
    est = Estimator(rect, 3, 2, limits=limit)
    expected = Estimator(rect, 3, 2, start=start, limits=limit)
    result = est.cut()
    assert len(result) == 1
    result = result[0]
    assert result.rectangle == expected.rectangle
    assert result.trp == expected.trp
    assert result.tlp == expected.tlp
    assert result.height == expected.height
    assert result.g_height == expected.g_height
    assert result.start == expected.start
    assert result.limits == expected.limits


@pytest.mark.parametrize(
    'limit',
    [None, (15, 0), (0, 15), (15, 15)]
)
def test_cut_lim_4_unlimited(limit):
    """Тест на разрез прямоугольника без ограничений"""
    rect = Rectangle((0, 0), (7, 5))
    est = Estimator(rect, 3, 2, limits=limit)
    result = est.cut()
    assert len(result) == 4
    expected = (
        [(0, 5), (2.5, 7)], [(7, 0), (7.5, 3.5)],
        [(0, 5), (2.5, 10.5)], [(7, 0), (5, 3.5)]
    )
    for i, (start, limits) in enumerate(expected):
        exp = Estimator(rect, 3, 2, start=start, limits=limits)
        assert result[i].rectangle == exp.rectangle
        assert result[i].trp == exp.trp
        assert result[i].tlp == exp.tlp
        assert result[i].height == exp.height
        assert result[i].g_height == exp.g_height
        assert result[i].start == exp.start
        assert result[i].limits == exp.limits


@pytest.mark.parametrize(
    'limit, expected',
    [
        [
            (7, 0),
            [
                [(0, 5), (2, 7)], [(7, 0), (7, 3.5)],
                [(0, 5), (2, 10.5)], [(7, 0), (5, 3.5)]
            ]
        ],
        [
            (0, 8),
            [
                [(0, 5), (2.5, 7)], [(7, 0), (7.5, 1)],
                [(0, 5), (2.5, 8)], [(7, 0), (5, 1)]
            ]
        ],
        [
            (7, 9),
            [
                [(0, 5), (2, 7)], [(7, 0), (7, 2)],
                [(0, 5), (2, 9)], [(7, 0), (5, 2)]
            ]
        ],
    ]
)
def test_cut_lim_4(limit, expected):
    """Тест на разрез прямоугольника с учетом ограничений"""
    rect = Rectangle((0, 0), (7, 5))
    est = Estimator(rect, 3, 2, limits=limit)
    result = est.cut()
    assert len(result) == 4
    for i, (start, limits) in enumerate(expected):
        exp = Estimator(rect, 3, 2, start=start, limits=limits)
        assert result[i].rectangle == exp.rectangle
        assert result[i].trp == exp.trp
        assert result[i].tlp == exp.tlp
        assert result[i].height == exp.height
        assert result[i].g_height == exp.g_height
        assert result[i].start == exp.start
        assert result[i].limits == exp.limits


@pytest.mark.parametrize(
    'point',
    [(7, 5), (0, 0), (8, 6)]
)
def test_estimate_hem_end_without(point):
    """Тестирование кромок/торцов без ограничений"""
    rect = Rectangle((0, 0), (7, 5))
    est = Estimator(rect, 3, 1)
    result = est.estimate_hem_end(*point)
    assert result == (0, 0)


@pytest.mark.parametrize(
    'x_hem, point, expected',
    [
        [(0, 1), (7, 5), (1, 1.875)],
        [(0, 1), (5, 5), (1, 1.875)],
        [(0, 1), (7, 3), (1, 1.875)],
        [(0, 1), (3, 3), (1, 1.875)],
        [(0, 1), (0, 0), (1, 1.875)],
        [(0, 1), (7, 7), (1, 1.875)],
        [(0, 1), (7.3, 5), (1, 1.7329592341970628)],
        [(0, 1), (8, 6), (1, 1.458333333333334)],
    ]
)
def test_estimate_right_hem(x_hem, point, expected):
    """Тестирование правой кромки"""
    rect = Rectangle((0, 0), (7, 5))
    est = Estimator(rect, 3, 1, x_hem=x_hem)
    result = est.estimate_hem_end(*point)
    assert result == expected


@pytest.mark.parametrize(
    'y_hem, point, expected',
    [
        [(0, 1), (7, 5), (3.5, 1)],
        [(0, 1), (5, 5), (3.5, 1)],
        [(0, 1), (7, 3), (3.5, 1)],
        [(0, 1), (3, 3), (3.5, 1)],
        [(0, 1), (0, 0), (3.5, 1)],
        [(0, 1), (7, 6), (2.5, 1)],
        [(0, 1), (7.3, 5), (3.5, 1)],
        [(0, 1), (8, 6), (2.5, 1)],
    ]
)
def test_estimate_top_hem(y_hem, point, expected):
    """Тестирование верхней кромки"""
    rect = Rectangle((0, 0), (7, 5))
    est = Estimator(rect, 3, 1, y_hem=y_hem)
    result = est.estimate_hem_end(*point)
    assert result == expected


@pytest.mark.parametrize(
    'x_hem, y_hem, point, expected',
    [
        [(0, 1), (0, 1), (7, 5), (3.5, 1.875)],
        [(0, 1), (0, 1), (5, 5), (3.5, 1.875)],
        [(0, 1), (0, 1), (7, 3), (3.5, 1.875)],
        [(0, 1), (0, 1), (3, 3), (3.5, 1.875)],
        [(0, 1), (0, 1), (0, 0), (3.5, 1.875)],
        [(0, 1), (0, 1), (7, 6), (2.5, 1.875)],
        [(0, 1), (0, 1), (7.5, 5), (3.5, 1.6470588235294112)],
        [(0, 1), (0, 1), (14, 5), (3.5, 1)],
        [(0, 1), (0, 1), (8, 6), (2.5, 1.458333333333334)],
    ]
)
def test_estimate_hem_end(x_hem, y_hem, point, expected):
    """Тестирование верхней и правой кромок"""
    rect = Rectangle((0, 0), (7, 5))
    est = Estimator(rect, 3, 1, x_hem=x_hem, y_hem=y_hem)
    result = est.estimate_hem_end(*point)
    assert result == expected


@pytest.mark.parametrize(
    'x_hem, y_hem, point',
    [
        [(0, 1), (0, 1), (11, 11)],
        [(0, 1), (0, 1), (15, 6.5)],
        [(0, 1), (0, 1), (7.5, 12.5)],
    ]
)
def test_estimate_hem_end_none(x_hem, y_hem, point):
    """Тестирование верхней и правой кромок"""
    rect = Rectangle((0, 0), (7, 5))
    est = Estimator(rect, 3, 1, x_hem=x_hem, y_hem=y_hem)
    assert est.estimate_hem_end(*point) == (None, None)
