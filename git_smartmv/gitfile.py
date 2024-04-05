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


class GitFile():
    """A file or a directory."""

    def __init__(self, path: os.PathLike):
        self.path = Path(path)

    def is_tracked_by_git(self):
        """Determines if the path is tracked by Git.

        Returns:
            True if the path is being tracked by Git, False otherwise.
        """
        path = self.path

        try:
            cmd = ["git", "-C", str(self.git_toplevel()),
                   "ls-files", "--error-unmatch", "--", str(path.absolute())]
        except GitError:
            return False

        try:
            subprocess.check_call(cmd,
                                  stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            return False

        return True

    def git_toplevel(self) -> Path:
        """Finds the top-level Git directory for the given path.

        Raises:
            GitError: If the path is not inside a Git repository.

        Returns:
            The Path object pointing to the top-level Git directory.
        """
        if not self.path.exists():
            raise GitError(f"No such file or directory: '{self.path}'")

        cmd = ["git", "rev-parse", "--show-toplevel"]
        try:
            output = subprocess.check_output(
                cmd,
                stderr=subprocess.DEVNULL,
                cwd=self.path.parent if self.path.is_file() else self.path,
            )
            git_repo_path = Path(output.splitlines()[0].decode())
            if not git_repo_path.exists():
                raise IndexError
        except (IndexError, subprocess.CalledProcessError) as err:
            err_str = f"The file is not in a Git directory: '{self.path}'"
            raise GitError(err_str) from err

        return git_repo_path
