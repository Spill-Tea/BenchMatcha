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

"""Test algorithmic complexity module."""

import numpy as np
import pytest

from BenchMatcha import complexity as comp
from BenchMatcha.utils import _simple_stats


@pytest.fixture
def fit_result() -> comp.FitResult:
    return comp.FitResult(
        bigo="N",
        params=np.asarray([2.73]),
        cov=np.asarray([1.5]),
        rms=0.479,
    )


@pytest.fixture
def coords() -> tuple[np.ndarray, np.ndarray]:
    x = np.arange(3)
    y = np.arange(9).reshape((3, 3))

    return x, y


def test_fit_result_repr(fit_result: comp.FitResult) -> None:
    """minor test of fit result repr dunder method."""
    result: str = repr(fit_result)
    assert result == "FitResult(bigo=N,params=[2.730E+00],cov=[1.500E+00],rms=0.479)", (
        "Unexpected FitResult repr."
    )


@pytest.mark.parametrize(
    ["x", "y", "k", "expected"],
    [
        (np.arange(3), np.arange(5, 8), 1, 6.12372),
        (np.arange(3), np.arange(5, 8), 2, 8.66025),
    ],
)
def test_rmsd_computation(
    x: np.ndarray,
    y: np.ndarray,
    k: int,
    expected: float,
) -> None:
    """Confirm computation of mean normalized rmsd."""
    result: float = comp.compute_rmsd(x, y, k)
    assert isinstance(result, float), "Expected float return type."
    assert np.isclose(result, expected), "Unexpected rmsd computation."


def test_fit(coords: tuple[np.ndarray, np.ndarray]) -> None:
    """Test (linear) curve fitting."""
    x, y = coords
    mean, std = _simple_stats(y)
    result = comp.fit(comp.linear, "N", x, mean, std)

    assert isinstance(result, comp.FitResult), "Expected a fit result return type."
    assert result.bigo == "N", "Expected correct label."

    assert len(result.params) == 2, "Expected 2 parameters."
    assert np.allclose(result.params, np.asarray([3.0, 1.0])), (
        "Unexpected param values."
    )

    assert len(result.cov) == 2, "Expected 2 parameter errors."
    assert np.allclose(result.cov, np.asarray([0.7071, 0.91287])), (
        "Unexpected param error values."
    )

    assert np.isclose(result.rms, 0.0), "Unexpected error."


def test_analyze_complexity() -> None:
    """Test batch analysis of algorithmic complexity."""
    x = np.arange(10, 20)
    y = np.arange(1, 31).reshape(10, 3)
    result = comp.analyze_complexity(x, y)
    assert isinstance(result, list), "Expected list return type."
    assert len(result) == 6, "Expected 6 elements"
    assert all(isinstance(x, comp.FitResult) for x in result), (
        "Expected all elements to be a FitResult type."
    )

    # Results should be sorted by best performing fit, by minimizing rmsd.
    assert comp.get_best_fit(result) == result[0], "Expected same FitResult."
