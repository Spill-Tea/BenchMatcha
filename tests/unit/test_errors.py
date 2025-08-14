import builtins
from collections.abc import Callable, Iterator
from json import JSONDecodeError

import pytest

from BenchMatcha import errors


@pytest.fixture
def register_error() -> Iterator[Callable[[type[Exception]], type[Exception]]]:
    e: type[Exception] | None = None

    def inner(exc: type[Exception]) -> type[Exception]:
        nonlocal e
        e = errors.register_custom_exception(exc)

        return e

    yield inner

    if e is not None:
        assert e in errors._exception_register, "Expected error to be registered"
        errors._exception_register.remove(e)
        assert e not in errors._exception_register, "Expected error to be removed."


def test_registering_custom_error(
    register_error: Callable[[type[Exception]], type[Exception]],
):
    """Confirm we can correctly register custom exception classes."""

    class CustomMagicalUnknownUnicornError(Exception): ...

    res = register_error(CustomMagicalUnknownUnicornError)
    assert res is CustomMagicalUnknownUnicornError, "Expected same exception."


# https://pytest-xdist.readthedocs.io/en/stable/known-limitations.html#order-and-amount-of-test-must-be-consistent
@pytest.mark.parametrize(
    "custom",
    sorted(  # limitation of pytest-xdist -> cannot handle unordered (sets) iterables
        filter(
            lambda x: not (hasattr(builtins, x.__name__) or x == JSONDecodeError),
            errors._exception_register,
        ),
        key=lambda x: x.__name__,
    ),
)
def test_custom_exception_api(custom: type[Exception]) -> None:
    """Test we conform to Custom exception API."""
    assert issubclass(custom, Exception), "Expected to subclass Exception."
    assert hasattr(custom, "response"), "Expected to have response method."


@pytest.mark.parametrize(
    ["cls", "args"],
    [
        [errors.ParsingError, ()],
        [errors.SchemaError, (1,)],
    ],
)
def test_custom_exception_response(cls: type[Exception], args: tuple | None) -> None:
    """Confirm response method returns an instance of the class."""
    result = cls.response(*args)
    assert isinstance(result, cls), (
        f"Expected to return an instance of exception: {cls.__name__}."
    )
