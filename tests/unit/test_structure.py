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
    """Temporarily modify supported versions, with teardown to reinstate original."""
    previous = structure.SUPPORTED_VERSIONS

    def modify(value: tuple[int, ...]) -> tuple[int, ...]:
        structure.SUPPORTED_VERSIONS = value
        return value

    yield modify

    structure.SUPPORTED_VERSIONS = previous
    assert structure.SUPPORTED_VERSIONS == previous


@pytest.fixture
def complexity_info() -> dict:
    """Expected complexity info data."""
    return {
        "function": "function",
        "big_o": "N",
        "cpu_coefficient": 1.2549524739108346e01,
        "real_coefficient": 1.2555517635286144e01,
        "rms": 5.4107447739157266e-02,
    }


@pytest.fixture
def cache_data() -> list[tuple]:
    """Expected cache data."""
    return [
        ("Data", 1, 65536, 0),
        ("Instruction", 1, 131072, 0),
        ("Unified", 2, 4194304, 1),
    ]


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


def _check_cache(cache: structure.Cache, expected: tuple) -> None:
    assert isinstance(cache, structure.Cache), f"Expected Cache type: {type(cache)}."
    assert cache.type == expected[0], f"Unexpected type: {cache.type}"
    assert cache.level == expected[1], f"Unexpected level: {cache.level}"
    assert cache.size == expected[2], f"Unexpected size: {cache.size}"
    assert cache.num_sharing == expected[3], f"Unexpected sharing: {cache.num_sharing}"


def test_convert_cache_data() -> None:
    """Test we correctly convert cache json data into a dataclass."""
    cache = {
        "type": "test",
        "level": 17,
        "size": 45,
        "num_sharing": 50,
        "unknown_key": 3,
    }
    result = structure.Cache.from_json(cache)
    _check_cache(result, ("test", 17, 45, 50))


def test_parse_cache_json_data(mock_data: str, cache_data: list[tuple]) -> None:
    """Test we correctly parse cache json data into a dataclass."""
    data: dict = load(mock_data)
    caches: list[dict] = data["context"]["caches"]
    for cache, e in zip(caches, cache_data, strict=False):
        result = structure.Cache.from_json(cache)
        _check_cache(result, e)


def _check_complexity_info(complexity: structure.ComplexityInfo, expected: dict):
    assert isinstance(complexity, structure.ComplexityInfo), (
        "Expected value to be a ComplexityInfo object."
    )
    assert complexity.function == expected["function"], (
        f"Incorrect Function Name: {complexity.function}"
    )
    assert complexity.big_o == expected["big_o"], (
        f"Incorrect Function Name: {complexity.function}"
    )
    assert complexity.cpu_coefficient == expected["cpu_coefficient"], (
        f"Unexpected CPU Coefficient: {complexity.cpu_coefficient}"
    )
    assert complexity.real_coefficient == expected["real_coefficient"], (
        f"Unexpected Real Coefficient: {complexity.real_coefficient}"
    )
    assert complexity.rms == expected["rms"], f"Unexpected RMS: {complexity.rms}"


def test_convert_benchmark_json_to_complexity(complexity_info: dict) -> None:
    """Test conversion of benchmark data correctly collects complexity info."""
    obj: list[dict] = [
        {
            "name": "function/repeats:3_BigO",
            "family_index": 0,
            "per_family_instance_index": 0,
            "run_name": "function/repeats:3",
            "run_type": "aggregate",
            "repetitions": 3,
            "threads": 1,
            "aggregate_name": "BigO",
            "aggregate_unit": "time",
            "cpu_coefficient": 1.2549524739108346e01,
            "real_coefficient": 1.2555517635286144e01,
            "big_o": "N",
            "time_unit": "ns",
        },
        {
            "name": "function/repeats:3_RMS",
            "family_index": 0,
            "per_family_instance_index": 0,
            "run_name": "function/repeats:3",
            "run_type": "aggregate",
            "repetitions": 3,
            "threads": 1,
            "aggregate_name": "RMS",
            "aggregate_unit": "percentage",
            "rms": 5.4107447739157266e-02,
        },
    ]

    result = structure.get_complexity_info(obj)
    assert isinstance(result, dict), "Expected dictionary object returned."
    assert "function" in result, "Expected function name key to be present."
    value = result["function"]
    _check_complexity_info(value, complexity_info)


def test_parse_full_json_data(
    mock_data: str,
    complexity_info: dict,
    cache_data: list[tuple],
) -> None:
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
    for c, e in zip(result.caches, cache_data, strict=False):
        _check_cache(c, e)

    assert result.load_avg == [4.69092, 4.60693, 4.47949]
    assert result.library_version == "1.9.4"
    assert result.library_build_type == "release"
    assert result.json_schema_version == 1
    assert result.aslr_enabled is False
    assert isinstance(result.python_version, str), "Expected a string"
    assert isinstance(result.git_sha, str), "Expected a string"

    assert isinstance(result.benchmarks, list), "Expected benchmarks to be a list."
    assert len(result.benchmarks) == 1
    _check_complexity_info(result.benchmarks[0].complexity, complexity_info)


def test_convert_benchmark_context_to_json(mock_data: str) -> None:
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
