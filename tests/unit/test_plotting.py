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

"""unit test plotting module."""

import tempfile

import numpy as np
import plotly.graph_objs as go
import pytest

from BenchMatcha import plotting


def test_serialization_to_html():
    """Confirm a plotly figure is saved to a html file."""
    figure = go.Figure()

    with tempfile.NamedTemporaryFile("w+") as file:
        plotting.to_html(figure, file.name)
        file.seek(0)
        data: str = file.read(1024)

    assert data.startswith("<div>"), "Expected html serialization."


def test_serialization_to_json():
    """Confirm a plotly figure is saved to a json file."""
    figure = go.Figure()

    with tempfile.NamedTemporaryFile("w+") as file:
        plotting.to_json(figure, file.name)
        file.seek(0)
        data: str = file.read(1024)

    assert data.startswith("{"), "Expected json serialization."


@pytest.mark.parametrize(
    ["x", "length", "vals", "labels"],
    [
        (
            np.asarray([2, 256]),
            9,
            [1, 2, 4, 8, 16, 32, 64, 128, 256],
            [
                "2<sup>0</sup>",
                "2<sup>1</sup>",
                "2<sup>2</sup>",
                "2<sup>3</sup>",
                "2<sup>4</sup>",
                "2<sup>5</sup>",
                "2<sup>6</sup>",
                "2<sup>7</sup>",
                "2<sup>8</sup>",
            ],
        ),
        (
            np.asarray([4, 4]),
            2,
            [2, 4],
            [
                "2<sup>1</sup>",
                "2<sup>2</sup>",
            ],
        ),
    ],
)
def test_construct_log2_axis(
    x: np.ndarray,
    length: int,
    vals: list[int],
    labels: list[str],
) -> None:
    """Confirm a log 2 axis is constructed correctly"""
    a, b = plotting.construct_log2_axis(x)

    assert len(a) == len(b) == length
    assert a == vals, "Incorrect values"
    assert b == labels, "Incorrect plotly labels."


def test_create_scatter_trace() -> None:
    """Confirm function constructs a plotly scatter trace."""
    x = np.arange(5)
    y = np.arange(25).reshape(5, 5)
    result = plotting.create_scatter_trace(x, y, "test", "black")
    assert isinstance(result, go.Scatter)


def test_create_box_plot() -> None:
    """Confirm function constructs a plotly box plot trace."""
    x = np.arange(5)
    y = np.arange(25).reshape(5, 5)
    result = plotting.box_plot(x, y, "test", "black", "red")
    assert isinstance(result, go.Box)


def test_create_annotation_text() -> None:
    """Test construction of plot annotation data."""
    result = plotting.create_annotation_text("test", 1.0)
    assert isinstance(result, dict), "expected a dictionary return type."
    assert "text" in result, "Expected text annotation key."


@pytest.mark.parametrize(
    ["key"],
    [["(1)"], ["N"], ["lgN"], ["NlgN"], ["N^2"], ["N^3"], ["invalid"]],
)
def test_get_big_o_function(key: str) -> None:
    """Test retrieval of complexity function."""
    result = plotting.get_big_o_function(key)
    assert callable(result), "Expected a callable."


def test_draw_complexity_line() -> None:
    """Confirm function produces a scatter trace."""
    x = np.arange(20)
    result = plotting.draw_complexity_line(x, 1.2, "N", "test", "red")
    assert isinstance(result, go.Scatter)
