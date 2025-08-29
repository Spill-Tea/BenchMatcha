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

"""Integration test suite for cli runner entry point."""

import os
from collections.abc import Callable

import pytest


HERE: str = os.path.abspath(os.path.dirname(__file__))
DATA: str = os.path.join(HERE, "data")


def _assert_cache_created(cache: str, status: int) -> None:
    assert os.path.exists(cache), "Expected cache directory to be created."
    assert os.path.isdir(cache), "expected path to be a directory."
    assert os.path.exists(os.path.join(cache, "out.html")), (
        "expected figures to be generated."
    )

    # NOTE: this output is temporary.
    assert os.path.exists(os.path.join(cache, "benchmark.json")), (
        "expected data to be saved."
    )
    assert status == 0, "Expected no errors."


@pytest.mark.parametrize(
    ["path"],
    [
        (os.path.join(DATA, "single"),),  # Directory with single file
        (os.path.join(DATA, "single", "bench_a.py"),),  # single file
        (
            os.path.join(DATA, "handle_imports"),
        ),  # Directory with file that imports locally
    ],
)
def test_bench_directory(
    path: str,
    benchmark: Callable[[list[str]], tuple[int, str, str, str]],
) -> None:
    """Test benchmarking a directory of benchmark suites."""
    status, out, error, tmpath = benchmark(["--path", path])

    cache: str = os.path.join(tmpath, ".benchmatcha")
    _assert_cache_created(cache, status)


@pytest.mark.parametrize(
    ["form"],
    [
        ("--benchmark_format=json",),  # frivolously provide format
        ("--benchmark_format=csv",),  # providing incorrect format is overridden
    ],
)
def test_json_key_val(
    form: str,
    benchmark: Callable[[list[str]], tuple[int, str, str, str]],
) -> None:
    """Confirm including benchmark format proceeds normally."""
    path: str = os.path.join(DATA, "single")
    status, out, error, tmpath = benchmark([form, "--path", path])

    cache: str = os.path.join(tmpath, ".benchmatcha")
    _assert_cache_created(cache, status)


def _setup_pyproject(x: str):
    p: str = os.path.join(x, "pyproject.toml")
    with open(p, "w") as f:
        ...


def test_empty_pyproject_config_file(
    benchmark: Callable[[list[str], Callable[[str], None]], tuple[int, str, str, str]],
) -> None:
    """Perform run with empty pyproject config."""
    path: str = os.path.join(DATA, "single")

    status, out, error, tmpath = benchmark(["--path", path], _setup_pyproject)
    assert os.path.exists(os.path.join(tmpath, "pyproject.toml")), (
        "Expected pyproject config file to be setup."
    )

    cache: str = os.path.join(tmpath, ".benchmatcha")
    _assert_cache_created(cache, status)


@pytest.mark.parametrize(
    ["param", "value"],
    [
        ("--color", "red"),
        ("--line-color", "black"),
        ("--x-axis", "2"),
        ("--verbose", None),
    ],
)
def test_config_parameters(
    param: str,
    value: str | None,
    benchmark: Callable[[list[str], Callable[[str], None]], tuple[int, str, str, str]],
) -> None:
    """Test available cli flags to modify configuration."""
    path: str = os.path.join(DATA, "single")
    args: list[str] = ["--path", path, param]
    if value is not None:
        args.append(value)

    status, out, error, tmpath = benchmark(args)
    cache: str = os.path.join(tmpath, ".benchmatcha")
    _assert_cache_created(cache, status)

    if param == "--verbose":
        assert "DEBUG" in error, "Expected debug logging in stderr."
