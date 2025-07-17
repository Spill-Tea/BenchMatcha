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

"""Custom Pygment syntax highlighting style."""

from typing import ClassVar

from pygments.style import Style
from pygments.token import (
    Comment,
    Error,
    Keyword,
    Name,
    Number,
    Operator,
    Other,
    Punctuation,
    String,
    Text,
    _TokenType,
)
from utils import get_brackets


def bold(color: str) -> str:
    """Embolden color."""
    return f"bold {color}"


def italic(color: str) -> str:
    """Italicize color."""
    return f"italic {color}"


def underline(color: str) -> str:
    """Underline text with color."""
    return f"underline {color}"


class Colors:
    """Define colors used more than once."""

    datatype: str = "#61C8B0"
    variable: str = "#9CDCFE"
    function: str = "#DCDCAA"
    reserved: str = "#639BD4"
    default: str = "#D4D4D4"
    control: str = "#C586C0"
    builtin: str = "#4EC9B0"
    declare: str = "#569CD6"
    problem: str = "#C3726A"
    comment: str = "#6A9955"
    bracket: str = "#F9C922"


class VSCodeDarkPlus(Style):
    """Custom theme deeply inspired by VSCode Dark+ as a pygments style."""

    background_color: str = "#1E1E1E"

    styles: ClassVar[dict[_TokenType, str]] = {  # pyright: ignore
        # Comments
        Comment: Colors.comment,
        Comment.Single: Colors.comment,
        Comment.Preproc: Colors.reserved,
        Comment.Special: bold(Colors.declare),
        Comment.Hashbang: italic("#7C7046"),
        Comment.Multiline: italic("#525252"),
        # Keywords
        Keyword: Colors.control,
        Keyword.Type: Colors.datatype,
        Keyword.Declare: bold(Colors.declare),
        Keyword.Constant: bold(Colors.declare),
        Keyword.Reserved: Colors.declare,
        Keyword.Namespace: Colors.control,
        # Variable Names
        Name: Colors.variable,
        Name.Type: Colors.builtin,
        Name.Class: Colors.datatype,
        Name.Builtin: Colors.builtin,
        Name.Builtin.Pseudo: italic(Colors.variable),
        Name.Constant: "#4FC1FF",
        Name.Function: Colors.function,
        Name.Function.Magic: italic(Colors.function),
        Name.Variable: Colors.variable,
        Name.Variable.Class: Colors.datatype,
        Name.Variable.Magic: Colors.function,
        Name.Namespace: Colors.datatype,
        Name.Exception: Colors.problem,
        # (Doc)Strings
        Text: Colors.default,
        String: "#C9937A",
        String.Doc: italic(Colors.comment),
        String.Doc.Title: bold("#80AE6B"),
        String.Affix: Colors.declare,
        String.Regex: "#D16969",
        String.Escape: "#D7BA7D",
        String.Interpol: Colors.declare,
        # Numbers
        Number: "#B6CEA9",
        Number.Other: Colors.declare,
        # Operators
        Operator: Colors.default,
        Operator.Word: Colors.control,
        # Punctuation
        Punctuation: Colors.default,
        **get_brackets(
            [
                Colors.bracket,
                "#EA2EEA",
                "#5DCD4C",
                "#3B9ADE",
            ]
        ),
        Punctuation.Error: underline("#F92222"),
        # Miscellaneous
        Error: underline(bold(Colors.problem)),
        Other: Colors.default,
    }
