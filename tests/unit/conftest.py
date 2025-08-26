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

import tempfile
from collections.abc import Iterator

import pytest


@pytest.fixture
def mock_context() -> str:
    return """
"context": {
    "date": "2025-07-13T12:09:31-07:00",
    "host_name": "host",
    "executable": "file.py",
    "num_cpus": 12,
    "mhz_per_cpu": 24,
    "cpu_scaling_enabled": false,
    "caches": [
      {
        "type": "Data",
        "level": 1,
        "size": 65536,
        "num_sharing": 0
      },
      {
        "type": "Instruction",
        "level": 1,
        "size": 131072,
        "num_sharing": 0
      },
      {
        "type": "Unified",
        "level": 2,
        "size": 4194304,
        "num_sharing": 1
      }
    ],
    "load_avg": [4.69092,4.60693,4.47949],
    "library_version": "1.9.4",
    "library_build_type": "release",
    "json_schema_version": 1
  },
"""


@pytest.fixture
def mock_bench() -> str:
    return """
"benchmarks": [
    {
      "name": "function/8/repeats:3",
      "family_index": 0,
      "per_family_instance_index": 0,
      "run_name": "function/8/repeats:3",
      "run_type": "iteration",
      "repetitions": 3,
      "repetition_index": 0,
      "threads": 1,
      "iterations": 1686012,
      "real_time": 4.2350600595475760e+02,
      "cpu_time": 4.2322355950016964e+02,
      "time_unit": "ns"
    },
    {
      "name": "function/8/repeats:3",
      "family_index": 0,
      "per_family_instance_index": 0,
      "run_name": "function/8/repeats:3",
      "run_type": "iteration",
      "repetitions": 3,
      "repetition_index": 1,
      "threads": 1,
      "iterations": 1686012,
      "real_time": 4.2872337197514543e+02,
      "cpu_time": 4.2800703672334481e+02,
      "time_unit": "ns"
    },
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
      "cpu_coefficient": 1.2549524739108346e+01,
      "real_coefficient": 1.2555517635286144e+01,
      "big_o": "N",
      "time_unit": "ns"
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
      "rms": 5.4107447739157266e-02
    }
]
"""


@pytest.fixture
def mock_data(mock_context: str, mock_bench: str) -> str:
    """mock benchmark data."""
    return "{" + f"{mock_context}{mock_bench}" + "}"


@pytest.fixture
def mock_file(mock_data: str) -> Iterator[tempfile._TemporaryFileWrapper]:
    with tempfile.NamedTemporaryFile("w+") as f:
        f.write(mock_data)
        f.seek(0)

        yield f
