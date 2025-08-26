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


@pytest.mark.parametrize(
    ["path"],
    [
        (os.path.join(DATA, "single"),),
        (os.path.join(DATA, "handle_imports"),),
    ],
)
def test_bench_directory(
    path: str,
    benchmark: Callable[[list[str]], tuple[int, str, str, str]],
) -> None:
    """Test benchmarking a directory of benchmark suites."""
    status, out, error, tmpath = benchmark([path])
    if len(error):
        print(error)

    cache: str = os.path.join(tmpath, ".benchmatcha")

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
    assert len(error) == 0, "Expected no errors"
