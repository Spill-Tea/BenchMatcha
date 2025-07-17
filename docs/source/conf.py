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

"""Sphinx configuration file."""

import os
import sys

from sphinx.application import Sphinx
from sphinx.highlighting import lexer_classes as _lexer_registry


sys.path.insert(0, os.path.abspath("../src/"))  # Required to see python package
sys.path.append(os.path.abspath("./_ext"))  # Required for custom extensions


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project = "PyTemplate"
copyright = "2025, Jason C Del Rio (Spill-Tea)"
author = "Jason C Del Rio (Spill-Tea)"
release = "v0.0.1"


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.viewcode",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx_multiversion",
]

napoleon_google_docstring = True  # Use google docstring format (sphinx.ext.napoleon)
autosummary_generate = True  # Turn on sphinx.ext.autosummary
smv_branch_whitelist = "^(main|dev)$"
smv_tag_whitelist = (
    r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"  # standard semvar version
    r"(?:-("
    r"(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*"
    r"))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

templates_path = ["_templates"]
exclude_patterns = []

# Use custom syntax highlighting (style)
pygments_style = "styles.VSCodeDarkPlus"
pygments_dark_style = "styles.VSCodeDarkPlus"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
# https://pradyunsg.me/furo/customisation/
html_theme = "furo"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
# html_logo = "_static/logo.svg"
github_url = "https://github.com/Spill-Tea/PyTemplate"

# Theme options
html_theme_options = {
    "light_logo": "_static/logo.svg",
    "dark_logo": "_static/logo-dark.svg",
    "footer_icons": [
        {
            "name": "GitHub",
            "url": github_url,
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "fa-brands fa-solid fa-github fa-2x",
            "target": "_blank",
        },
    ],
}

html_sidebars = {
    "**": [
        "sidebar/brand.html",  # overwritten
        "sidebar/search.html",
        "sidebar/scroll-start.html",
        "sidebar/navigation.html",
        "sidebar/versions.html",  # added
        "sidebar/scroll-end.html",
    ],
}
html_additional_pages = {"page": "page.html"}


def setup(app: Sphinx) -> None:
    """Custom sphinx application startup setup."""
    from lexers import CustomCythonLexer, CustomPythonLexer  # type: ignore

    # NOTE: overwrite default python and cython lexers
    app.add_lexer("python", CustomPythonLexer)
    assert "python" in _lexer_registry, "python language not found in registry"
    assert _lexer_registry["python"] == CustomPythonLexer, (
        "custom Python Lexer not found in registry."
    )

    app.add_lexer("cython", CustomCythonLexer)
    assert "cython" in _lexer_registry, "cython language not found in registry"
    assert _lexer_registry["cython"] == CustomCythonLexer, (
        "custom Cython Lexer not found in registry."
    )
