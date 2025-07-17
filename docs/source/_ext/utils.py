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

"""Common shared utility functions."""

from typing import Iterator

from pygments.token import _TokenType, string_to_tokentype


def get_bracket_level(n: int) -> _TokenType:
    """Retrieve the bracket depth level token."""
    name: str = f"Punctuation.Level{n}"

    return string_to_tokentype(name)


def nbrackets(n: int) -> Iterator[_TokenType]:
    """Dynamically generate tokentype to identify a variable number of brackets."""
    for j in range(n):
        yield get_bracket_level(j)


def dynamic_brackets(colors: list[str]) -> list[tuple[_TokenType, str]]:
    """Dynamically generate bracket color options from a list of colors."""
    return [(key, colors[idx]) for idx, key in enumerate(nbrackets(len(colors)))]


def get_brackets(colors: list[str]) -> dict[_TokenType, str]:
    """Get brackets in dictionary form."""
    return dict(dynamic_brackets(colors))
