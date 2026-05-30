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
import toml
from attrs import define, field

from BenchMatcha import config


@pytest.fixture
def toml_inner() -> dict:
    return {
        "color": "#FFF",
        "line_color": "#333",
        "font": "Courier",
        "x_axis": 5,
        "unsupported_key": "test",
    }


@pytest.fixture
def toml_data(toml_inner: dict) -> dict:
    """Mock toml config as a dictionary object."""
    return {"tool": {"BenchMatcha": toml_inner}}


@pytest.fixture
def toml_str(toml_data: dict) -> str:
    """Mock toml config text."""
    return toml.dumps(toml_data)


@pytest.fixture
def configuration() -> config.ConfigBase:
    """Create configuration and reset instance singleton."""
    return config.ConfigBase()


@pytest.mark.parametrize(
    ["obj", "keys", "expected"],
    [
        ({}, ("a", "b", "c"), {}),
        ({"a": {"b": {"c": "d"}}}, ("a", "b", "c"), "d"),
        ({"a": {"b": {"d": "d"}}}, ("a", "b", "c"), {}),
    ],
)
def test_traverse(obj: dict, keys: tuple[str], expected: str) -> None:
    """Test dictionary traversal works as anticipated."""
    result = config.traverse(obj, keys)
    assert result == expected


def test_config_load(
    toml_str: str,
    toml_data: dict,
    configuration: config.ConfigBase,
) -> None:
    """Confirm toml data loads correctly."""
    with StringIO(toml_str) as stream:
        instance = config.ConfigUpdater(stream, configuration)
        result = instance.load()

    assert result == toml_data, "Expected same object"


def _assert_config_is_updated(conf: config.ConfigBase) -> None:
    assert conf.color == "#FFF", "Expected color to be updated."
    assert conf.line_color == "#333", "Expected line color to be updated."
    assert conf.font == "Courier", "Expected font to be updated."
    assert not hasattr(conf, "unsupported_key"), (
        "Expected unsupported key to be bypassed."
    )


def test_config_private_update(
    toml_inner: dict,
    configuration: config.ConfigBase,
) -> None:
    """Confirm config data is updated correctly."""
    instance = config.ConfigUpdater("", configuration)
    instance._update(toml_inner)
    _assert_config_is_updated(configuration)


def test_config_update(
    toml_str: str,
    configuration: config.ConfigBase,
) -> None:
    """Confirm toml data loads correctly."""
    with StringIO(toml_str) as stream:
        instance = config.ConfigUpdater(stream, configuration)
        instance.update()

    _assert_config_is_updated(configuration)


def test_config_json(
    toml_str: str,
    toml_inner: dict,
    configuration: config.ConfigBase,
) -> None:
    """Confirm configuration returns as json object correctly."""
    with StringIO(toml_str) as stream:
        instance = config.ConfigUpdater(stream, configuration)
        instance.update()

    _assert_config_is_updated(configuration)
    toml_inner.pop("unsupported_key", None)
    assert configuration.tojson() == toml_inner, "Unexpected json object data."


@patch.object(config.ConfigUpdater, "load")
def test_config_update_mock(
    mock: MagicMock,
    toml_data: dict,
    configuration: config.ConfigBase,
) -> None:
    """Confirm config is updated by mocking load method of ConfigUpdater."""
    mock.return_value = toml_data
    instance = config.ConfigUpdater("", configuration)
    instance.update()
    _assert_config_is_updated(configuration)


@patch.object(config.ConfigUpdater, "load")
def test_config_update_function(
    mock: MagicMock,
    toml_data: dict,
    configuration: config.ConfigBase,
) -> None:
    """Confirm config is updated from available function api."""
    mock.return_value = toml_data
    config.update_config_from_pyproject("", configuration)
    _assert_config_is_updated(configuration)


def test_config_base_setters(configuration: config.ConfigBase) -> None:
    """Confirm class setattr engages designated converters."""
    configuration.x_axis = "5"
    assert isinstance(configuration.x_axis, int), "Expected value to be coerced to int."
    assert configuration.x_axis == 5, "Expected value to be updated to 5."

    setattr(configuration, "x_axis", "7")  # noqa: B010
    assert configuration.x_axis == 7, "Expected value to be updated to 7."


@define
class A(config._ConfigBase):
    a: str = field(default="a")
    b: int = field(default=1)


@define
class B(config._ConfigBase):
    a: A = field(factory=A)
    b: str = field(default="b")


@pytest.fixture
def toml_data_b() -> str:
    return """
[tool.BenchMatcha]
b = "loaded b"

[tool.BenchMatcha.a]
a = "loaded a"
b = 5
"""


@patch.object(config.ConfigUpdater, "load")
def test_recursive_update_function(
    mock: MagicMock,
    toml_data_b: str,
):
    """Confirm nested recursive configurations are appropriately updated."""
    # sanity checks
    con = B()
    assert con.a.a == "a"
    assert con.a.b == 1
    assert con.b == "b"

    # setup
    data: dict = toml.loads(toml_data_b)
    mock.return_value = data

    instance = config.ConfigUpdater("", con)
    instance.update()

    # checks
    assert con.a.a == "loaded a"
    assert con.a.b == 5
    assert con.b == "loaded b"

    # sanity
    assert instance.config is con, "Expected config to be same on instance."
