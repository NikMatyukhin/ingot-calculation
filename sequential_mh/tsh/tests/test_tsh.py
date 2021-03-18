import pytest

from ..bpp_ts import Estimator
from ..rect import Point, Rectangle


@pytest.mark.parametrize(
    'r, h0, h1, p, expect',
    [
        (Rectangle((0, 0), (4, 6)), 2, 1, (0, 0), (8, 12)),
        (Rectangle((0, 0), (4, 6)), 2, 1, (8, 0), (0, 6)),
        (Rectangle((0, 0), (4, 6)), 2, 1, (8, 1), (0, 5)),
        (Rectangle((0, 0), (4, 6)), 2, 1, (0, 12), (4, 0)),
        (Rectangle((0, 0), (4, 6)), 2, 1, (2, 12), (2, 0)),
        (Rectangle((0, 0), (4, 6)), 2, 1, (4, 12), (0, 0)),
        (Rectangle((0, 0), (4, 6)), 2, 1, (8, 6), (0, 0)),
        (Rectangle((0, 0), (4, 6)), 2, 1, (0, 8), (6, 4)),
        (Rectangle((0, 0), (4, 6)), 2, 1, (5, 0), (3, 9.6)),
        (Rectangle((0, 0), (4, 6)), 2, 1, (6, 8), (0, 0)),
        (Rectangle((0, 0), (4, 6)), 2, 1, (5, 9.6), (0, 0)),
    ]
)
def test_est_boundaries(r, h0, h1, p, expect):
    est = Estimator(r, h0, h1)
    assert est(*p) == expect


@pytest.mark.parametrize(
    'r, h0, h1, p, expect',
    [
        (Rectangle((0, 0), (4, 6)), 2, 1, (1, 1), (7, 11)),
        (Rectangle((0, 0), (4, 6)), 2, 1, (4, 6), (4, 6)),
        (Rectangle((0, 0), (4, 6)), 2, 1, (6, 6), (2, 2)),
        (Rectangle((0, 0), (4, 6)), 2, 1, (4, 8), (2, 4)),
        (Rectangle((0, 0), (4, 6)), 2, 1, (2, 8), (4, 4)),
        (Rectangle((0, 0), (4, 6)), 2, 1, (6, 3), (2, 5)),
        (Rectangle((0, 0), (4, 6)), 2, 1, (5, 8), (1, 1.6)),
    ]
)
def test_est(r, h0, h1, p, expect):
    est = Estimator(r, h0, h1)
    x, y = est(*p)
    assert x == expect[0]
    assert pytest.approx(y, 0.01) == expect[1]


@pytest.mark.parametrize(
    'r, h0, h1, p, expect',
    [
        (Rectangle((0, 0), (4, 6)), 2, 1, (0, 15), None),
        (Rectangle((0, 0), (4, 6)), 2, 1, (2, 13), None),
        (Rectangle((0, 0), (4, 6)), 2, 1, (4, 16), None),
        (Rectangle((0, 0), (4, 6)), 2, 1, (9, 0), None),
        (Rectangle((0, 0), (4, 6)), 2, 1, (10, 2), None),
        (Rectangle((0, 0), (4, 6)), 2, 1, (11, 6), None),
        (Rectangle((0, 0), (4, 6)), 2, 1, (8, 8), None),
        (Rectangle((0, 0), (4, 6)), 2, 1, (9, 9), None),
        (Rectangle((0, 0), (4, 6)), 2, 1, (10, 8), None),
    ]
)
def test_est_negative(r, h0, h1, p, expect):
    est = Estimator(r, h0, h1)
    res = est(*p)
    assert res is None


@pytest.mark.parametrize(
    'r, h0, h1, expect',
    [
        (Rectangle((0, 0), (4, 6)), 2, 1, ((8, 6), (4, 12))),
        (Rectangle((1, 1), (4, 6)), 2, 1, ((7, 6), (4, 11))),
    ]
)
def test_est_tlp_trp_property(r, h0, h1, expect):
    est = Estimator(r, h0, h1)
    tlp = est.tlp
    trp = est.trp
    assert isinstance(tlp, Point)
    assert isinstance(trp, Point)
    assert trp == expect[0]
    assert tlp == expect[1]


@pytest.mark.parametrize(
    'r, h0, h1, expect',
    [
        (Rectangle((0, 0), (4, 6)), 2, 1, (12, 8)),
        (Rectangle((1, 1), (4, 6)), 2, 1, (10, 6)),
    ]
)
def test_est_max_length_width(r, h0, h1, expect):
    est = Estimator(r, h0, h1)
    assert est.max_length == expect[0]
    assert est.max_width == expect[1]


@pytest.mark.parametrize(
    'r, h0, h1, expect',
    [
        (Rectangle((0, 0), (4, 6)), 2, 1, (6, 4)),
    ]
)
def test_est_min_length_width(r, h0, h1, expect):
    est = Estimator(r, h0, h1)
    assert est.min_length == expect[0]
    assert est.min_width == expect[1]


@pytest.mark.parametrize(
    'r, h0, h1, rect',
    [
        (Rectangle((0, 0), (4, 6)), 2, 1, Rectangle((0, 0), (4, 12))),
        (Rectangle((0, 0), (4, 6)), 2, 1, Rectangle((0, 0), (8, 6))),
        (Rectangle((0, 0), (4, 6)), 2, 1, Rectangle((0, 0), (5, 9.6))),
    ]
)
def test_update_boundaries(r, h0, h1, rect):
    est = Estimator(r, h0, h1)
    est.update(rect)
    assert est.height == h1
    assert est.rectangle == rect


@pytest.mark.parametrize(
    'r, h0, h1, rect, expect',
    [
        (Rectangle((0, 0), (4, 6)), 2, 1, Rectangle((0, 0), (4, 8)), 1.5),
        (Rectangle((0, 0), (4, 6)), 2, 1, Rectangle((0, 0), (5, 6)), 1.6),
        (Rectangle((0, 0), (4, 6)), 2, 1, Rectangle((0, 0), (5, 8)), 1.2),
    ]
)
def test_update(r, h0, h1, rect, expect):
    est = Estimator(r, h0, h1)
    est.update(rect)
    assert est.height == expect
    assert est.rectangle == rect


@pytest.mark.parametrize(
    'r, h0, h1, rect',
    [
        (Rectangle((0, 0), (4, 6)), 2, 1, Rectangle((0, 0), (2, 13))),
        (Rectangle((0, 0), (4, 6)), 2, 1, Rectangle((0, 0), (4, 14))),
        (Rectangle((0, 0), (4, 6)), 2, 1, Rectangle((0, 0), (10, 3))),
        (Rectangle((0, 0), (4, 6)), 2, 1, Rectangle((0, 0), (10, 6))),
        (Rectangle((0, 0), (4, 6)), 2, 1, Rectangle((0, 0), (8, 8))),
        (Rectangle((0, 0), (4, 6)), 2, 1, Rectangle((0, 0), (9, 9))),
        (Rectangle((0, 0), (4, 6)), 2, 1, Rectangle((0, 0), (10, 8))),
    ]
)
def test_update_raise(r, h0, h1, rect):
    est = Estimator(r, h0, h1)
    with pytest.raises(ValueError):
        est.update(rect)
