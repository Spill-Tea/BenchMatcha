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

"""Primary Benchmark Runner."""

import logging
import os
import sys
from json import JSONDecodeError

import google_benchmark as gbench
import orjson
import plotly.graph_objs as go  # type: ignore[import-untyped]
from wurlitzer import pipes  # type: ignore[import-untyped]

from . import plotting
from .config import Config, update_config_from_pyproject
from .errors import ParsingError
from .handlers import HandleText
from .sifter import collect_benchmarks, load_benchmark
from .structure import BenchmarkArray, BenchmarkContext, parse_version


log: logging.Logger = logging.getLogger(__name__)


def manage_registration(path: str) -> None:
    """Manage import, depending on whether path is a directory or file."""
    abspath: str = os.path.abspath(path)
    if not os.path.exists(abspath):
        raise FileNotFoundError("Invalid filepath")

    if os.path.isdir(abspath):
        collect_benchmarks(abspath)

    elif os.path.isfile(abspath) and abspath.endswith(".py"):
        load_benchmark(abspath, os.path.abspath(os.path.dirname(abspath)))

    else:
        log.warning(
            "Unsupported path provided. While the path does exist, it is neither a"
            " file nor a directory."
        )


def plot_benchmark_array(benchmark: BenchmarkArray) -> go.Figure:
    """Plot benchmark array."""
    fig = go.Figure()
    fig.add_trace(
        plotting.create_scatter_trace(
            benchmark.size,
            benchmark.cpu_time,
            "CPU Time",
            Config.color,
        )
    )

    fig.add_trace(
        plotting.draw_complexity_line(
            benchmark.size,
            benchmark.complexity.cpu_coefficient,
            benchmark.complexity.big_o,
            f"CPU Time Fit ({benchmark.complexity.big_o})",
            Config.line_color,
        )
    )

    fig.add_annotation(
        **plotting.create_annotation_text(
            benchmark.complexity.big_o,
            benchmark.complexity.rms,
        )
    )

    vals, labels = plotting.construct_log2_axis(benchmark.size)
    if (p := len(vals) // 13) > 0:
        vals = vals[:: p + 1]
        labels = labels[:: p + 1]

    fig.update_layout(
        title=f"Benchmark Results<br><i>{benchmark.function}</i>",
        xaxis=dict(
            type="log",
            tickvals=vals,
            ticktext=labels,
            tickmode="array",
            title="Input Size (n)",
        ),
        yaxis=dict(
            title=f"Time ({benchmark.unit})",
            type="log",
            dtick=1,
            exponentformat="power",
        ),
        legend_title="Timing",
        font=dict(
            family=Config.font,
            size=12,
        ),
    )

    return fig


def _run() -> BenchmarkContext:
    # TODO: Improve logic here (e.g. --benchmark_format=csv)
    if "--benchmark_format=json" not in sys.argv:
        sys.argv.append("--benchmark_format=json")

    # TODO: create python bindings of library to call and collect json data without
    #       serializing and capturing stdout.
    # Read this excellent blog regarding redirecting stdout from c libraries:
    # https://eli.thegreenplace.net/2015/redirecting-all-kinds-of-stdout-in-python/
    with pipes() as (stdout, stderr):
        try:
            gbench.main()

        # NOTE: bypass sys.exit(0) call from main
        except SystemExit:
            ...

    text: str = stdout.read()
    stdout.close(), stderr.close()  # pylint: disable=W0106

    handler = HandleText(text)
    try:
        obj: dict = handler.handle()
    except JSONDecodeError as e:
        raise ParsingError.response() from e

    context: BenchmarkContext = parse_version(obj)

    return context


def save(context: BenchmarkContext, cache_dir: str) -> None:
    """Save benchmark data."""
    for j in context.benchmarks:
        figure: go.Figure = plot_benchmark_array(j)
        plotting.to_html(figure, os.path.join(cache_dir, "out.html"), "a")

    # TODO: Save data to database. Serialize to json in the interim.
    database: str = os.path.join(cache_dir, "benchmark.json")
    data: list[dict] = []
    if os.path.exists(database):
        with open(database, "br") as f:
            data = orjson.loads(f.read())

    data.append(context.to_json())
    serialized: bytes = orjson.dumps(
        data,
        option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_SERIALIZE_DATACLASS,
    )

    with open(database, "bw") as f:
        f.write(serialized)


def run(path: str, cache_dir: str) -> None:
    """BenchMatcha Runner."""
    manage_registration(path)

    # TODO: remove arguments specific to BenchMatch to prevent failure on google
    #       benchmark interface.

    context: BenchmarkContext = _run()
    save(context, cache_dir)


# TODO: Handle a list of separated filepaths.
def run_paths(paths: list[str]) -> None:
    """Run benchmarks against a list of paths."""
    for path in paths:
        manage_registration(path)

    context: BenchmarkContext = _run()


def main() -> None:
    """Primary CLI Entry Point."""
    # TODO: support specification of config file path from CLI, to overwrite default
    # TODO: Support command line args to overwrite default config.
    cwd: str = os.getcwd()
    p = os.path.join(cwd, ".pyproject.toml")
    if os.path.exists(p):
        update_config_from_pyproject(p)

    # Create cache if does not exist
    cache = os.path.join(cwd, ".benchmatcha")
    if not os.path.exists(cache):
        os.mkdir(cache)

    # TODO: Determine if a list of paths have been provided instead, and handle
    run(sys.argv.pop(), cache)
