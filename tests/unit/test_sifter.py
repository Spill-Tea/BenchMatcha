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

"""Unit test BenchMatcha.sifter module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from BenchMatcha import sifter


class MockDirEntry:
    """mock os.DirEntry object."""

    path: str
    directory: bool

    def __init__(self, path: str, directory: bool = False):
        self.path = path
        self.directory = directory

    def is_dir(self, **kwargs) -> bool:
        return self.directory

    def __str__(self):
        return self.path

    def __eq__(self, value: MockDirEntry) -> bool:
        return value.path == self.path and value.directory == self.directory


@patch.object(sifter.Collector, "get")
@patch.object(sifter, "scandir")
def test_collect(mock_scandir: MagicMock, mock_get: MagicMock):
    """Unit test sifter.collect method."""
    mock_scandir.side_effect = [
        iter(
            (
                MockDirEntry("root/bench_this.py"),
                MockDirEntry("root/other.py"),
                MockDirEntry("root/sub", True),
            )
        ),
        iter(
            (
                MockDirEntry("root/sub/bench_sub.py"),
                MockDirEntry("root/sub/bench_sub2.py"),
            )
        ),
    ]
    mock_get.side_effect = [
        iter(("root/bench_this.py",)),
        iter(("root/sub/bench_sub.py", "root/sub/bench_sub2.py")),
    ]

    result: list[str] = list(sifter.collect("root"))
    assert len(result) == 3, "Expected 3 results."

    expected = [
        "root/bench_this.py",
        "root/sub/bench_sub.py",
        "root/sub/bench_sub2.py",
    ]

    for a, b in zip(result, expected, strict=False):
        assert a == b, "Unexpected DirEntry."

    assert len(set(result).difference(set(expected))) == 0, "expected identical output."
