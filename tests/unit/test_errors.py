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
