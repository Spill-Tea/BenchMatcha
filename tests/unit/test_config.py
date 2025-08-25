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

"""Test config module."""

from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from BenchMatcha import config


@pytest.fixture
def toml_str() -> str:
    return """
[tool.BenchMatcha]
color="#FFF"
line_color="#333"
font="Courier"
upsupported_key="test"
"""


@pytest.fixture
def toml_data() -> dict:
    return {
        "tool": {
            "BenchMatcha": {
                "color": "#FFF",
                "line_color": "#333",
                "font": "Courier",
                "upsupported_key": "test",
            }
        }
    }


def test_config_load(toml_str: str, toml_data: dict) -> None:
    """Confirm toml data loads correctly."""
    with StringIO(toml_str) as stream:
        instance = config.ConfigUpdater(stream)
        result = instance.load()

    assert result == toml_data, "Expected same object"


def _assert_config_is_updated():
    assert config.Config.color == "#FFF", "Expected color to be updated."
    assert config.Config.line_color == "#333", "Expected line color to be updated."
    assert config.Config.font == "Courier", "Expected font to be updated."


def test_config_private_update(toml_data: dict) -> None:
    """Confirm config data is updated correctly."""
    instance = config.ConfigUpdater("")
    instance._update(toml_data)
    _assert_config_is_updated()


def test_config_update(toml_str: str) -> None:
    """Confirm toml data loads correctly."""
    with StringIO(toml_str) as stream:
        instance = config.ConfigUpdater(stream)
        instance.update()
    _assert_config_is_updated()


@patch.object(config.ConfigUpdater, "load")
def test_config_update_mock(mock: MagicMock, toml_data: dict) -> None:
    """Confirm config is updated by mocking load method of ConfigUpdater."""
    mock.return_value = toml_data
    instance = config.ConfigUpdater("")
    instance.update()
    _assert_config_is_updated()


@patch.object(config.ConfigUpdater, "load")
def test_config_update_function(mock: MagicMock, toml_data: dict) -> None:
    """Confirm config is updated from available function api."""
    mock.return_value = toml_data
    config.update_config_from_pyproject("")
    _assert_config_is_updated()
