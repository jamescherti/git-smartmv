#!/usr/bin/env python
#
# Copyright (C) James Cherti
# URL: https://github.com/jamescherti/git-smartmv
#
# Distributed under terms of the GNU General Public License version 3.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
"""A command-line tool that can decide whether to use `git mv` or `mv`."""

import os
import subprocess
from pathlib import Path


class GitError(Exception):
    """Error with Git."""


class File():
    """A file or a directory."""

    def __init__(self, path: os.PathLike):
        self.path = Path(path)

    def is_tracked_by_git(self):
        """Return True if 'path' is being tracked by Git."""
        path = self.path

        try:
            cmd = ["git", "-C", str(self.git_toplevel()),
                   "ls-files", "--error-unmatch", str(path.absolute())]
        except GitError:
            return False

        cwd = path
        if path.is_file():
            cwd = path.parent.absolute()

        try:
            subprocess.check_call(cmd,
                                  stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL,
                                  cwd=cwd)
        except subprocess.CalledProcessError:
            return False

        return True

    def git_toplevel(self) -> Path:
        """Return the top-level Git directory of 'path'."""
        path = self.path
        err_str = f"The file is not in a Git directory: '{path}'"

        if not path.exists():
            raise GitError(err_str)

        path = path.absolute()

        if path.is_file():
            cwd = path.parent
        else:
            cwd = path

        cmd = ["git", "rev-parse", "--show-toplevel"]
        try:
            output = subprocess.check_output(
                cmd,
                stderr=subprocess.DEVNULL,
                cwd=cwd,
            )
        except subprocess.CalledProcessError as err:
            raise GitError(err_str) from err

        try:
            git_repo_path = Path(output.splitlines()[0].decode())
        except IndexError as err:
            raise GitError(err_str) from err

        if not git_repo_path.exists():
            raise GitError(err_str)

        return git_repo_path
