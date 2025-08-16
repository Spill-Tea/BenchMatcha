"""Miscellaneous utilities."""

from __future__ import annotations

import enum
import sys

import numpy as np


def power_of_2(x: int) -> int:
    """Retrieve the next power of 2, if value is not already one."""
    x -= 1
    mod: int = 1
    size: int = sys.getsizeof(x)
    while mod < size:
        x |= x >> mod
        mod *= 2

    return x + 1


def _simple_stats(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Compute mean and standard deviation."""
    mean: np.ndarray = np.nanmean(x, axis=1)
    std: np.ndarray = np.nanstd(x, axis=1, ddof=1)

    return mean, std


# https://github.com/google/benchmark/blob/main/src/complexity.cc#L52-L69
class BigO(str, enum.ReprEnum):
    """Big o notation string identifiers."""

    o1 = "(1)"
    oN = "N"
    oNSquared = "N^2"
    oNCubed = "N^3"
    oLogN = "lgN"
    oNLogN = "NlgN"
    oLambda = "f(N)"

    @classmethod
    def get(cls, value: str) -> str:
        # e.g. "o1" -> "(1)"
        return cls[value].value

    @classmethod
    def back(cls, value: str) -> str:
        # e.g. "(1)" -> "o1"
        return cls(value).name
