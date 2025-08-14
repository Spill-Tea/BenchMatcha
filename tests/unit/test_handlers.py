"""Test json data handlers module."""

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
