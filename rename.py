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

"""Primitive script to update repository (project) name throughout template.

Arguments:
    new-name (str): new project name (defaults to root directory name)
    old-name (str): old project name (defaults to PyTemplate)
    path (str): root path of project (defaults to cwd)
    dry-run (bool): print out what files / directories would be modified
    timeout (int): Time in seconds to allow a subprocess to run.

Notes:
    * client must have git installed.

"""

import argparse
import os
import subprocess
from collections.abc import Iterator


def bypass(path: str, git_root: str, timeout: int = 1) -> bool:
    """Use git to identify if a path is ignored as specified by a .gitignore file."""
    # NOTE: Do not capture errors to avoid assuming a path is included or not.
    result = subprocess.run(
        ["git", "-C", git_root, "check-ignore", path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
        timeout=timeout,
    )

    return result.returncode == 0


def find_git_root(start_path: str, timeout: int = 1) -> str:
    """Confirm we are in a git repository."""
    try:
        result = subprocess.run(
            ["git", "-C", start_path, "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        raise RuntimeError("This script must be run inside a Git repository.") from e


def safe_scandir(path: str) -> Iterator[os.DirEntry]:
    """Wrapper around os.scandir."""
    try:
        with os.scandir(path) as it:
            yield from it
    except PermissionError:
        return


def replace_in_file(
    filepath: str,
    old: str,
    new: str,
    dry_run: bool = False,
) -> int:
    """Replace an old keyword found within a file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except (UnicodeDecodeError, FileNotFoundError) as e:
        print(f"[Warning] ({e.__class__.__name__}) {filepath}")
        return 0

    if old not in content:
        return 0

    if dry_run:
        print(f"[DRY RUN] Would update content within file: {filepath}")

    else:
        new_content: str = content.replace(old, new)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated content within file: {filepath}")

    return 1


def update_project_name(
    path: str,
    old_name: str,
    new_name: str,
    dry_run: bool,
    git_root: str,
    timeout: int = 1,
) -> int:
    """Recursively search, and modify files in place to update project name if used."""
    count = 0
    for entry in safe_scandir(path):
        full_path = os.path.join(path, entry.name)

        if bypass(full_path, git_root, timeout):
            continue

        if entry.is_dir(follow_symlinks=False):
            count += update_project_name(
                full_path, old_name, new_name, dry_run, git_root
            )

        elif entry.is_file(follow_symlinks=False):
            count += replace_in_file(full_path, old_name, new_name, dry_run)

    return count


def _filetype(entry: os.DirEntry) -> str:
    key: str = ""
    if entry.is_file(follow_symlinks=False):
        key = " filepath"
    elif entry.is_dir(follow_symlinks=False):
        key = " directory"

    return key


def rename_directories_and_files(
    path: str,
    old_name: str,
    new_name: str,
    dry_run: bool,
    git_root: str,
    timeout: int = 1,
) -> int:
    """Rename both directories and filenames alike if old keyword present."""
    count: int = 0
    for entry in safe_scandir(path):
        full_path = os.path.join(path, entry.name)
        if bypass(full_path, git_root, timeout):
            continue

        # NOTE: Depth First Search. Handle all children before renaming a directory.
        if entry.is_dir(follow_symlinks=False):
            count += rename_directories_and_files(
                full_path, old_name, new_name, dry_run, git_root
            )

        if old_name not in entry.name:
            continue

        new_path = os.path.join(path, entry.name.replace(old_name, new_name))
        key: str = _filetype(entry)
        if dry_run:
            print(f"[DRY RUN] Would rename{key}: {full_path} -> {new_path}")
        else:
            os.rename(full_path, new_path)
            print(f"Renamed{key}: {full_path} -> {new_path}")
        count += 1

    return count


def parse_args() -> argparse.Namespace:
    """Define and return parsed arguments."""
    parser = argparse.ArgumentParser(description="Rename a Python project template.")
    parser.add_argument(
        "--new-name",
        help="New project name (e.g. my_project)",
    )
    parser.add_argument(
        "--old-name",
        default="PyTemplate",
        help="Old project name to replace (optional, defaults to PyTemplate)",
    )
    parser.add_argument(
        "--path",
        default=".",
        help="Root path of the project (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change, but don't modify anything",
    )
    parser.add_argument(
        "--timeout",
        default=1,
        help="Time in seconds to allow a subprocess to run.",
        type=int,
    )

    return parser.parse_args()


def main() -> None:
    """Main script Entry point."""
    args: argparse.Namespace = parse_args()
    git_root: str = find_git_root(args.path)

    # NOTE: When this template is forked, the project should be renamed. So we can
    #       reasonably assume the name of the new project. Report assumption to client.
    if args.new_name is None:
        args.new_name = os.path.basename(git_root)
        print(f"Assuming new project name: {args.new_name}")

    if args.new_name == args.old_name:
        print("Exiting. Both New and old names are identical.")
        return

    print(
        f"Project Found at: '{args.path}'",
        f"Replacing '{args.old_name}' --> '{args.new_name}'",
        sep="\n",
    )
    if args.dry_run:
        print("[DRY RUN] Confirming Dry Run Mode. No changes will be made.")

    # NOTE: this script may also be updated to reflect the new project name.
    total: int = 0
    print("\nStep I: Update File contents.")
    total += update_project_name(
        args.path,
        args.old_name,
        args.new_name,
        dry_run=args.dry_run,
        git_root=git_root,
        timeout=args.timeout,
    )
    print("\nStep II: Update Filepath Names.")
    total += rename_directories_and_files(
        args.path,
        args.old_name,
        args.new_name,
        dry_run=args.dry_run,
        git_root=git_root,
        timeout=args.timeout,
    )

    if args.dry_run:
        print(f"\n[DRY RUN] Complete. Would modify {total} file(s).")
    else:
        print(f"Success. Modified {total} file(s) in total.")


if __name__ == "__main__":
    main()
