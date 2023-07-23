from assertpy import assert_that

from core.calc import add, subtract


def test_add():
    result = add(2, 3)
    assert_that(result).is_equal_to(5)


def test_subtract():
    result = subtract(10, 2)
    assert_that(result).is_equal_to(8)
