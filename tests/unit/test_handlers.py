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

"""Test json data handlers module."""

import tempfile
from collections.abc import Callable
from io import BytesIO, StringIO
from typing import IO, Any

import pytest

from BenchMatcha import handlers


def test_load(mock_data: str) -> None:
    """Test load interface."""
    result = handlers.load(mock_data)
    assert isinstance(result, dict), "Expected to load a dict."


@pytest.mark.parametrize(
    ["handler", "transformer"],
    [
        (handlers.HandlePath, lambda x: x),
        (handlers.HandleBytes, lambda x: x.encode()),
        (handlers.HandleIO, lambda x: StringIO(x)),
        (handlers.HandleIO, lambda x: BytesIO(x.encode())),
    ],
)
def test_handlers(
    handler: type[handlers.Handler],
    transformer: Callable[[str], Any],
    mock_data: str,
) -> None:
    """"""
    mock = transformer(mock_data)
    result = handler(mock).handle()
    assert isinstance(result, dict), "Expected a dictionary loaded."
    assert isinstance(handlers.dispatch(mock), handler), (
        "Expected sample handler object."
    )

    if isinstance(mock, (StringIO, BytesIO)):
        mock.close()


def test_stream_type_error():
    """Confirm a type error is raised when an unreadable stream is provided."""
    with pytest.raises(TypeError) as err, tempfile.NamedTemporaryFile("w") as file:
        handlers.HandleIO(file)

    assert err.type is TypeError, "Expected a TypeError to be raised."


@pytest.mark.parametrize(
    ["handler", "transformer", "expected"],
    [
        (handlers.dispatch, lambda x: x.name, handlers.HandlePath),
        (handlers.dispatch, lambda x: x.read(), handlers.HandlePath),
        (handlers.dispatch, lambda x: x.read().encode(), handlers.HandleBytes),
        (handlers.dispatch, lambda x: x, handlers.HandleIO),
    ],
)
def test_file_path_handlers(
    handler: Callable[[Any], handlers.Handler],
    transformer: Callable[[IO], Any],
    expected: handlers.Handler,
    mock_file: IO,
) -> None:
    """Test dispatch handlers."""
    result: handlers.Handler = handler(transformer(mock_file))
    assert isinstance(result, expected), "Unexpected Handler dispatched."
    data = result.handle()
    assert isinstance(data, dict), "Expected dictionary object."


def test_dispatch_unsupported_object() -> None:
    """Test we raise TypeError when providing unsupported object."""
    with pytest.raises(TypeError) as e:
        handlers.dispatch(1)

    assert e.type is TypeError, "Expected a type error."
