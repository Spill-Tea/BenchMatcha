"""Discovery of benchmark tests to register."""

import glob
import os
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType

from _pytest.pathlib import import_path


def scandir(filepath: str) -> Iterator[os.DirEntry[str]]:
    """Simple wrapper around os.scandir to use more simply as an iterator."""
    with os.scandir(os.path.abspath(filepath)) as scanner:
        yield from scanner


def collect(root: str, pattern: str = "bench*.py") -> Iterator[str]:
    """Collect relevant filepaths recursively stemming from root directory."""
    yield from glob.iglob(os.path.join(root, pattern), root_dir=root)

    for candidate in scandir(root):
        if candidate.is_dir(follow_symlinks=False):
            yield from collect(candidate.path, pattern)


def load_benchmark(path: str, root: str) -> ModuleType:
    """Load a benchmark suite."""
    return import_path(
        os.path.abspath(path),
        root=Path(root).absolute().resolve(),
        consider_namespace_packages=False,
    )


def collect_benchmarks(root: str) -> None:
    """Collect all benchmarks from a variety of benchmark suites."""
    root = os.path.abspath(root)
    for j in collect(root):
        load_benchmark(j, root=root)
