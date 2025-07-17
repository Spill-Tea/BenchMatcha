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

"""Customized python lexer."""

from collections import deque
from collections.abc import Iterator
from typing import ClassVar

from pygments.lexer import bygroups, combined, include, words
from pygments.lexers.python import CythonLexer, PythonLexer, RegexLexer
from pygments.token import (
    Comment,
    Keyword,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Text,
    Whitespace,
    _TokenType,
)
from utils import get_bracket_level


def _find(it, obj, key=lambda a, b: a == b) -> int:
    for n, j in enumerate(it):
        if key(j, obj):
            return n
    raise IndexError("Unable to find object.")


def _get_index(n: int):
    def inner(a, b) -> bool:
        return a[n] == b

    return inner


class MixinLexer(RegexLexer):
    """Regex Mixin Lexer class.

    Notes:
        1. Supports primitive rainbow bracket coloring.
        2. Supports primitive constant declaration (uppercase variables)

    """

    n_brackets: int
    _stack: deque[int]

    def __init__(self, **options) -> None:
        self.n_brackets = int(options.pop("n_brackets", 4))
        super().__init__(**options)
        self._stack = deque[int]()

    def _enter(self) -> _TokenType:
        """Retrieve next token in cycle."""
        idx = len(self._stack) % self.n_brackets
        self._stack.append(idx)

        return get_bracket_level(idx)

    def _exit(self) -> _TokenType:
        """Remove element from stack and return token."""
        try:
            idx: int = self._stack.pop()
            return get_bracket_level(idx)

        # NOTE: Only additional ending brackets trigger this (e.g. `{{ }}}` ).
        # NOTE: We are not attempting to detect correct matching brackets (e.g. `(]` )
        except IndexError:
            return Punctuation.Error

    def get_tokens_unprocessed(
        self,
        text,
        stack=("root",),
    ) -> Iterator[tuple[int, _TokenType, str]]:
        _token: _TokenType
        for idx, token, value in super().get_tokens_unprocessed(text, stack):
            _token = token
            if token is Name and value.isupper():
                _token = Name.Constant

            elif token is Punctuation:
                match value:
                    case "(" | "[" | "{" | "<":
                        _token = self._enter()
                    case "}" | "]" | ")" | ">":
                        _token = self._exit()
                    case _:
                        ...

            yield idx, _token, value


docstrings: list = [
    (  # single line docstrings (edge case)
        r'^(\s*)([rRuUbB]{,2})("""(?:.)*?""")',
        bygroups(Whitespace, String.Affix, String.Doc),
    ),
    (  # Modfied triple double quote docstrings to highlight docstring titles
        r'^(\s*)([rRuUbB]{,2})(""")',
        bygroups(Whitespace, String.Affix, String.Doc),
        "docstring-double-quotes",
    ),
    (  # Intentionally treat text encapsulated within single triple quotes as String
        r"^(\s*)([rRuUbB]{,2})('''(?:.|\n)*?''')",
        bygroups(Whitespace, String.Affix, String),
    ),
]

comments: list = [
    (r"\A#!.+$", Comment.Hashbang),
    # Format Special Common Keywords in Comments
    (
        r"(#\s*)(TODO|FIXME|NOTE|BUG|HACK|XXX)(.*$)",
        bygroups(Comment.Single, Comment.Special, Comment.Single),
    ),
    (r"#.*$", Comment.Single),
]


python_root: list = [
    (r"\n", Whitespace),
    *docstrings,
    *comments,
    (r"\\\n", Text),
    (r"\\", Text),
    include("keywords"),
    include("soft-keywords"),
    (
        r"(def)((?:\s|\\\s)+)",
        bygroups(Keyword.Declare, Whitespace),
        "funcname",
    ),
    (
        r"(class)((?:\s|\\\s)+)",
        bygroups(Keyword.Declare, Whitespace),
        "classname",
    ),
    (
        r"(from)((?:\s|\\\s)+)",
        bygroups(Keyword.Namespace, Whitespace),
        "fromimport",
    ),
    (
        r"(import)((?:\s|\\\s)+)",
        bygroups(Keyword.Namespace, Whitespace),
        "import",
    ),
    include("expr"),
]


python_tokens: dict[str, list] = PythonLexer.tokens.copy()
python_tokens["root"] = python_root
python_tokens["docstring-double-quotes"] = [
    (
        r"(?<=\n)(\s*)(Args|Attributes|Returns|Raises|"
        r"Examples|Yields|References|Notes|Equations)(:)(\s*)",
        bygroups(Whitespace, String.Doc.Title, String.Doc, Whitespace),
    ),
    (r'^\s*(?:""")', String.Doc, "#pop"),
    (r".+[\r\n]*", String.Doc),
]

# Tokenize function names when used (i.e. function calls)
# NOTE: Must be inserted before general `Name` token but after `Name.Builtins` token
# NOTE: Implementation limitations -> we cannot distinguish between class and function
#       calls using regex based parsing alone (i.e without semantic analysis).
python_tokens["name"].insert(
    _find(python_tokens["name"], Name, _get_index(1)),
    (r"\b([a-zA-Z_]\w*)(?=\s*\()", Name.Function),
)

# Tokenize segment of number literals declared in different base (non base 10)
python_tokens["numbers"] = [
    (
        r"(\d(?:_?\d)*\.(?:\d(?:_?\d)*)?|(?:\d(?:_?\d)*)?\.\d(?:_?\d)*)"
        r"([eE][+-]?\d(?:_?\d)*)?([jJ]?)",
        bygroups(Number.Float, Number.Float, Number.Other),
    ),
    (r"(\d(?:_?\d)*[eE][+-]?\d(?:_?\d)*)([jJ]?)", bygroups(Number.Float, Number.Other)),
    (r"(0[oO])((?:_?[0-7])+)", bygroups(Number.Other, Number.Oct)),
    (r"(0[bB])((?:_?[01])+)", bygroups(Number.Other, Number.Bin)),
    (r"(0[xX])((?:_?[a-fA-F0-9])+)", bygroups(Number.Other, Number.Hex)),
    (r"(\d(?:_?\d)*)([jJ]?)", bygroups(Number.Integer, Number.Other)),
]


class CustomPythonLexer(MixinLexer, PythonLexer):
    """Custom enhanced regex-based python lexer.

    Notes:
        1. Implemented a simple stack based rainbow bracket colorizer.
            * limitation: Only detects errors that close more brackets than it opens.
            * limitation: No attempt is made to confirm matching closing brackets.
        2. Highlight Docstring titles (assumes google docstring format)
        3. Improved highlighting function calls (with limitations)
        4. Modify display of number components which indicate a different base number.

    """

    tokens: ClassVar[dict[str, list]] = python_tokens


cython_root = [
    (r"\n", Whitespace),
    *docstrings,
    (r"[^\S\n]+", Text),
    *comments,
    (r"[]{}:(),;[]", Punctuation),
    (r"\\\n", Whitespace),
    (r"\\", Text),
    (r"(in|is|and|or|not)\b", Operator.Word),
    (r"(<)([a-zA-Z0-9.?]+)(>)", bygroups(Punctuation, Keyword.Type, Punctuation)),
    (r"!=|==|<<|>>|[-~+/*%=<>&^|.?]", Operator),
    (
        r"(from)(\d+)(<=)(\s+)(<)(\d+)(:)",
        bygroups(
            Keyword, Number.Integer, Operator, Whitespace, Operator, Name, Punctuation
        ),
    ),
    include("keywords"),
    (r"(def)(\s+)", bygroups(Keyword.Declare, Whitespace), "funcname"),
    (r"(property)(\s+)", bygroups(Keyword.Type, Whitespace), "funcname"),
    (r"(cp?def)(\s+)", bygroups(Keyword.Declare, Whitespace), "cdef"),
    (r"(ctypedef)(\s+)", bygroups(Keyword.Declare, Whitespace), "ctypedef"),
    (r"(cdef)(:)", bygroups(Keyword.Declare, Punctuation)),
    (
        r"(class|cppclass|struct)(\s+)",
        bygroups(Keyword.Declare, Whitespace),
        "classname",
    ),
    (r"(from)(\s+)", bygroups(Keyword.Namespace, Whitespace), "fromimport"),
    (r"(c?import)(\s+)", bygroups(Keyword.Namespace, Whitespace), "import"),
    include("builtins"),
    include("backtick"),
    ('(?:[rR]|[uU][rR]|[rR][uU])"""', String, "tdqs"),
    ("(?:[rR]|[uU][rR]|[rR][uU])'''", String, "tsqs"),
    ('(?:[rR]|[uU][rR]|[rR][uU])"', String, "dqs"),
    ("(?:[rR]|[uU][rR]|[rR][uU])'", String, "sqs"),
    ('[uU]?"""', String, combined("stringescape", "tdqs")),
    ("[uU]?'''", String, combined("stringescape", "tsqs")),
    ('[uU]?"', String, combined("stringescape", "dqs")),
    ("[uU]?'", String, combined("stringescape", "sqs")),
    include("name"),
    include("numbers"),
]

cython_tokens: dict[str, list] = CythonLexer.tokens.copy()
cython_tokens["root"] = cython_root
cython_tokens["numbers"] = python_tokens["numbers"]
cython_tokens["docstring-double-quotes"] = python_tokens["docstring-double-quotes"]
cython_tokens["name"].insert(
    _find(cython_tokens["name"], Name, _get_index(1)),
    (r"\b([a-zA-Z_]\w*)(?=\s*\()", Name.Function),
)
cython_tokens["cdef"] = [
    # include packed keyword
    (r"(public|readonly|extern|api|inline|packed|fused)\b", Keyword),
    # Specialize Name.Class vs Name.Function vs Name.Variable tokens
    (
        # include cppclass keyword
        r"(struct|enum|union|class|cppclass)\b(\s+)([a-zA-Z_]\w*)",
        bygroups(Keyword.Declare, Whitespace, Name.Class),
        "#pop",
    ),
    (r"([a-zA-Z_]\w*)(\s*)(?=\()", bygroups(Name.Function, Whitespace), "#pop"),
    (r"([a-zA-Z_]\w*)(\s*)(?=[:,=#\n]|$)", bygroups(Name.Variable, Whitespace), "#pop"),
    (r"([a-zA-Z_]\w*)(\s*)(,)", bygroups(Name.Variable, Whitespace, Punctuation)),
    (r"from\b", Keyword, "#pop"),
    (r"as\b", Keyword),
    (r":", Punctuation, "#pop"),
    (r'(?=["\'])', Text, "#pop"),
    (r"[a-zA-Z_]\w*", Keyword.Type),
    (r".", Text),
]
# Define new ctypedef context
cython_tokens["ctypedef"] = [
    (r"(public|readonly|extern|api|inline|packed|fused)\b", Keyword),
    (
        r"(\s*)([a-zA-Z_]\w*)(\s*)(:)",
        bygroups(Whitespace, Name.Class, Whitespace, Punctuation),
        "#pop",
    ),
    (
        r"(struct|enum|union|class|cppclass)(\s+)([a-zA-Z_]\w*)",
        bygroups(Keyword.Declare, Whitespace, Name.Class),
        "#pop",
    ),
    (
        r"([a-zA-Z_]\w*)(\s+)([a-zA-Z_]\w*)",
        bygroups(Keyword.Type, Whitespace, Name.Class),
        "#pop",
    ),
    (r"([a-zA-Z_]\w*)", Name.Class, "#pop"),
]
# Define Keyword.Constant token
cython_tokens["keywords"].append(
    (words(("True", "False", "None", "NULL"), suffix=r"\b"), Keyword.Constant)
)
cython_tokens["keywords"][_find(cython_tokens["keywords"], Keyword, _get_index(1))] = (
    words(
        (
            "assert",
            "async",
            "await",
            "break",
            "by",
            "continue",
            # "ctypedef",
            "del",
            "elif",
            "else",
            "except",
            "except?",
            "exec",
            "finally",
            "for",
            # "fused",
            "gil",
            "global",
            "if",
            "include",
            "lambda",
            "namespace",  # added
            "new",  # added - relevant for c++ syntax
            "noexcept",  # added
            "nogil",
            "pass",
            "print",
            "raise",
            "return",
            "try",
            "while",
            "yield",
            "as",
            "with",
        ),
        suffix=r"\b",
    ),
    Keyword,
)
# Redefine Name.Builtin.Pseudo token (to not include Keyword.Constant values)
cython_tokens["builtins"][
    _find(cython_tokens["builtins"], Name.Builtin.Pseudo, _get_index(1))
] = (r"(?<!\.)(self|cls|Ellipsis|NotImplemented)\b", Name.Builtin.Pseudo)
# Redefine Name.Builtin token to include additional types
cython_tokens["builtins"][
    _find(cython_tokens["builtins"], Name.Builtin, _get_index(1))
] = (
    words(
        (
            "__import__",
            "abs",
            "all",
            "any",
            "apply",
            "basestring",
            "bin",
            "bint",
            "bool",
            "buffer",
            "bytearray",
            "bytes",
            "callable",
            "char",  # added
            "chr",
            "classmethod",
            "cmp",
            "coerce",
            "compile",
            "complex",
            "delattr",
            "dict",
            "dir",
            "divmod",
            "double",  # added
            "enumerate",
            "eval",
            "execfile",
            "exit",
            "file",
            "filter",
            "float",
            "frozenset",
            "getattr",
            "globals",
            "hasattr",
            "hash",
            "hex",
            "id",
            "input",
            "int",
            "intern",
            "isinstance",
            "issubclass",
            "iter",
            "len",
            "list",
            "locals",
            "long",
            "map",
            "max",
            "min",
            "next",
            "object",
            "oct",
            "open",
            "ord",
            "pow",
            "property",
            "Py_ssize_t",
            "range",
            "raw_input",
            "reduce",
            "reload",
            "repr",
            "reversed",
            "round",
            "set",
            "setattr",
            "size_t",  # added
            "slice",
            "sorted",
            "staticmethod",
            "ssize_t",  # added
            "str",
            "sum",
            "super",
            "tuple",
            "type",
            "unichr",
            "unicode",
            "unsigned",
            "vars",
            "xrange",
            "zip",
        ),
        prefix=r"(?<!\.)",
        suffix=r"\b",
    ),
    Name.Builtin,
)


class CustomCythonLexer(MixinLexer, CythonLexer):
    """Custom enhanced regex-based cython lexer."""

    tokens: ClassVar[dict[str, list]] = cython_tokens
