# BSD 3-Clause License
#
# Copyright (c) 2025, Spill-Tea
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
