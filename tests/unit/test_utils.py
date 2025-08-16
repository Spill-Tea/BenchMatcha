import numpy as np
import pytest

from BenchMatcha import utils


_power2: list[tuple[int, int]] = [
    (0, 0),
    (1, 1),
]
for j in range(2, 24):
    value = 1 << j
    _power2.append((value - 1, value))
    _power2.append((value, value))
    _power2.append((value + 1, 1 << (j + 1)))


@pytest.mark.parametrize(["value", "expected"], _power2)
def test_power_of_2(value: int, expected: int):
    """Test returns next power of two."""
    result = utils.power_of_2(value)
    assert result == expected, f"Unexpected result: {result}"


def test_simple_stats():
    """Test mean and std."""
    x = np.asarray([[1, 2, 3], [2, 3, 1], [3, 1, 2]])
    result = utils._simple_stats(x)
    assert isinstance(result, tuple), "Expected a tuple."
    assert np.all(result[0] == np.asarray([2, 2, 2]))
    assert np.all(result[1] == np.asarray([1, 1, 1]))


@pytest.mark.parametrize(
    ["value", "expected"],
    [
        ("o1", "(1)"),
        ("oN", "N"),
        ("oNSquared", "N^2"),
        ("oNCubed", "N^3"),
        ("oLogN", "lgN"),
        ("oNLogN", "NlgN"),
        ("oLambda", "f(N)"),
    ],
)
def test_bigo_enum_get(value: str, expected: str):
    """Test conversion of big o notation identifier get classmethod."""
    result: str = utils.BigO.get(value)
    assert result == expected, "Unexpected result."


@pytest.mark.parametrize(
    ["value", "expected"],
    [
        ("(1)", "o1"),
        ("N", "oN"),
        ("N^2", "oNSquared"),
        ("N^3", "oNCubed"),
        ("lgN", "oLogN"),
        ("NlgN", "oNLogN"),
        ("f(N)", "oLambda"),
    ],
)
def test_bigo_enum_back(value: str, expected: str):
    """Test conversion of big o notation identifier back classmethod."""
    result: str = utils.BigO.back(value)
    assert result == expected, "Unexpected result."
