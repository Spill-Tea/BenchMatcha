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

"""Unit test structure module."""

from collections.abc import Callable, Iterator
from datetime import UTC, datetime

import pytest

from BenchMatcha import errors, structure
from BenchMatcha.handlers import load


@pytest.fixture
def shunt_version() -> Iterator[Callable[[tuple[int, ...]], tuple[int, ...]]]:
    previous = structure.SUPPORTED_VERSIONS

    def modify(value: tuple[int, ...]) -> tuple[int, ...]:
        structure.SUPPORTED_VERSIONS = value
        return value

    yield modify

    structure.SUPPORTED_VERSIONS = previous
    assert structure.SUPPORTED_VERSIONS == previous


@pytest.mark.parametrize(
    ["value", "expected"],
    [
        ("2025-07-13T12:09:31-07:00", datetime(2025, 7, 13, 19, 9, 31, tzinfo=UTC)),
        ("2025-07-12T14:01:22+07:00", datetime(2025, 7, 12, 7, 1, 22, tzinfo=UTC)),
    ],
)
def test_parse_datetime(value: str, expected: datetime) -> None:
    """Test parsing of ISO8601 format datetime string."""
    result = structure.parse_datetime(value)
    assert isinstance(result, datetime), "Expected datetime object."
    assert result == expected, "Unexpected date time."


def test_parse_json_data(mock_data: str) -> None:
    """Test we correctly parse json data into a dataclass."""
    data = load(mock_data)
    result = structure.BenchmarkContext.from_json(data)
    assert isinstance(result, structure.BenchmarkContext)
    assert result.date == datetime(2025, 7, 13, 19, 9, 31, tzinfo=UTC)
    assert result.host_name == "host"
    assert result.executable == "file.py"
    assert result.num_cpus == 12
    assert result.mhz_per_cpu == 24

    assert result.cpu_scaling_enabled is False
    assert len(result.caches) == 3
    assert result.load_avg == [4.69092, 4.60693, 4.47949]
    assert result.library_version == "1.9.4"
    assert result.library_build_type == "release"
    assert result.json_schema_version == 1

    assert len(result.benchmarks) == 1


def test_convert_BenchmarkContext_to_json(mock_data: str) -> None:
    """Test we convert dataclass into dictionary json like objects."""
    data = load(mock_data)
    obj = structure.BenchmarkContext.from_json(data)
    result = obj.to_json()
    assert isinstance(result, dict), "Expected a dictionary object."

    caches = result["caches"]
    assert isinstance(caches, list)
    assert all(isinstance(i, dict) for i in caches), (
        "Expected cache instances to be dictionary objects."
    )

    benchmarks = result["benchmarks"]
    assert isinstance(benchmarks, list)
    assert all(isinstance(i, dict) for i in benchmarks), (
        "Expected benchmark instances to be dictionary objects."
    )
    assert all(isinstance(k["complexity"], dict) for k in benchmarks), (
        "Expected benchmark complexity instances to be dictionary objects."
    )


def test_unavailable_version() -> None:
    """Confirm SchemaError is raised when unavailable version is passed."""
    record: dict = {"context": {"json_schema_version": -10}}
    with pytest.raises(errors.SchemaError) as err:
        structure.parse_version(record)

    assert err.type is errors.SchemaError, "Expected to raise a SchemaError."


def test_unsupported_version(shunt_version) -> None:
    """Confirm SchemaError is raised when unsupported version is passed."""
    shunt_version((-10,))

    record: dict = {"context": {"json_schema_version": -10}}
    with pytest.raises(errors.SchemaError) as err:
        structure.parse_version(record)

    assert err.type is errors.SchemaError, "Expected to raise a SchemaError."
