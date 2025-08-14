"""Custom BenchMatcha exception definitions.

Considerations:
    * All custom exceptions should be defined within this module for better project
      organization. This also prevents proliferation of custom errors as project scales.
    * Custom exceptions should define a class method named `response` to construct and
      standardize verbiage of output message. It has the nice side effect of providing
      example context for usage.
    * Before creating a custom error, determine if available exceptions can be used
      instead.

"""

from __future__ import annotations

from json import JSONDecodeError
from typing import Self, TypeVar


E = TypeVar("E", bound=Exception)

_exception_register: set[type[Exception]] = {
    TypeError,
    ValueError,
    RuntimeError,
    JSONDecodeError,
    FileNotFoundError,
}


def register_custom_exception(cls: type[E]) -> type[E]:
    """Register custom exceptions."""
    _exception_register.add(cls)

    return cls


@register_custom_exception
class SchemaError(Exception):
    """Unsupported json schema."""

    @classmethod
    def response(cls, version: str) -> Self:
        """Define standard response message."""
        msg: str = f"Unsupported json schema version: {version}"

        return cls(msg)


@register_custom_exception
class ParsingError(Exception):
    """Failed to parse json output (from Google Benchmark)."""

    @classmethod
    def response(cls) -> Self:
        """Define standard response message."""
        return cls(
            "Failed to parse json data. Please confirm benchmarks do not contain "
            "print statements or write to stdout, which can interfere with output."
        )
