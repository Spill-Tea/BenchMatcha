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

import os
import subprocess
import tempfile
from collections.abc import Callable, Iterator

import pytest


HERE: str = os.path.abspath(os.path.dirname(__file__))


# NOTE: Coverage cannot be captured of a subprocess while changing the CWD, without
#       use of the tool.coverage.run.patch argument setup to use `subprocess`. This was
#       not introduced until V7.10.3. See the following for details:
#       https://github.com/nedbat/coveragepy/issues/1499
@pytest.fixture
def benchmark() -> Iterator[
    Callable[[list[str], Callable[[str], None] | None], tuple[int, str, str, str]]
]:
    """Benchmark entry point subprocess."""
    with tempfile.TemporaryDirectory(dir=HERE) as cursor:

        def inner(
            args: list[str],
            setup: Callable[[str], None] | None = None,
        ) -> tuple[int, str, str, str]:
            if setup is not None and callable(setup):
                setup(cursor)

            response: subprocess.CompletedProcess[bytes] = subprocess.run(
                ["benchmatcha", *args],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                cwd=cursor,
                env=os.environ,
            )
            output: str = response.stdout.decode()
            errors: str = response.stderr.decode()

            return response.returncode, output, errors, cursor

        yield inner
