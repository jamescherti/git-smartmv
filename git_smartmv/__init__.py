#!/usr/bin/env python
"""A command-line tool that can decide whether to use `git mv` or `mv`.

The `smartmv` is a command-line tool for moving files and directories without
having to worry about manually choosing whether to use `git mv` or `mv`.

The `smartmv` tool determines whether to use `git mv` or `mv` based on the
source and the destination path:
- If the file or directory is being moved within a Git repository,
  `smartmv` uses `git mv`.
- If the file is being moved between a Git repository and a non-Git directory
  or a different Git repository, the `smartmv` tool uses `mv`.

"""

import argparse
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path


class SmartmvError(Exception):
    """Error with `smartmv` command-line interface."""


class GitError(Exception):
    """Error with `git`."""


class Smartmv:
    """`smartmv` command-line interface."""

    cmd_git_timeout = 60
    exe_name = Path(sys.argv[0]).name

    def __init__(self):
        self._reset()

    def _reset(self):
        self._args = None
        self._cwd_git_toplevel = None

        self._source_paths = []
        self._dest_path = ""
        self._classified_source_paths = {"mv": [],
                                         "git mv": []}

        self._dest_git_repo = None
        self._mv_commands = {}

    def main(self):
        self._reset()

        try:
            self._cwd_git_toplevel = self.get_git_toplevel(".")
        except GitError:
            self._cwd_git_toplevel = None

        if not shutil.which("git"):
            err_str = f"{self.exe_name}: 'git': command not found"
            raise SmartmvError(err_str)

        # Main calls
        self._parse_args()
        logging.basicConfig(
            level=(logging.DEBUG if self._args.verbose else logging.INFO),
            stream=sys.stdout,
            format="[%(name)s] %(message)s")
        self._logger = logging.getLogger(self.exe_name)

        self._step1_parse_paths()
        self._step2_classify_paths()

        # Build mv commands
        self._step3_build_mv_commands()
        self._step4_warn_too_many_files()

        # Execute mv commands
        self._step5_execute_mv_commands()

    def _parse_args(self):
        desc = str(__doc__).splitlines()[0]
        usage = "%(prog)s [--option] [args]"
        parser = argparse.ArgumentParser(description=desc,
                                         usage=usage)
        parser.add_argument("files", metavar="N", type=str, nargs="+",
                            help="Files and/or directories")

        # Arguments that are not ignored
        list_opts = [
            ("-v", "--verbose"),
            ("-f", "--force"),
            ("-i", "--interactive"),
        ]

        # Arguments specific to smartmv
        parser.add_argument(
            "-w",
            "--warn-amount-files",
            type=int,
            required=False,
            default=-1,
            help=("This will raise a warning if the number of files"
                  "or directories being moved exceeds the specified amount"),
        )

        for opt, long_opt, help_str in list_opts:
            parser.add_argument(opt, long_opt, action="store_true",
                                default=False, help=help_str)

        self._args = parser.parse_args()
        if len(self._args.files) < 2:
            print(f"{self.exe_name}: missing destination file operand after "
                  f"'{self._args.files[0]}'", file=sys.stderr)
            sys.exit(1)

    def _step1_parse_paths(self):
        self._source_paths = [Path(item) for item in self._args.files[0: -1]]
        self._dest_path = Path(self._args.files[-1])
        self._logger.debug("source_paths: %s", str(self._source_paths))
        self._logger.debug("dest_path: %s", str(self._dest_path))

        if len(self._source_paths) > 1 and not self._dest_path.is_dir():
            print(f"{self.exe_name}: target '{self._dest_path}' is not a "
                  "directory", file=sys.stderr)
            sys.exit(1)

        try:
            if self._dest_path.exists():
                # The file/directory will be MOVED. Retrieve the the Git
                # top-level directory of the destination directory, and store
                # it in a variable.
                self._dest_git_repo = self.get_git_toplevel(self._dest_path)
            else:
                # The file/directory will be RENAMED. Retrieve the the Git
                # top-level directory of the parent directory, and store
                # it in a variable.
                self._dest_git_repo = self.get_git_toplevel(
                    self._dest_path.absolute().parent
                )
        except GitError:
            self._dest_git_repo = None  # Git error

        self._logger.debug("dest_git_repo: %s", str(self._dest_git_repo))

        for origin_path in self._source_paths:
            if not (origin_path.is_symlink() or origin_path.exists()):
                print(f"{self.exe_name}: cannot stat '{origin_path}': "
                      "No such file or directory", file=sys.stderr)
                sys.exit(1)

    def _step2_classify_paths(self):
        for origin_path in self._source_paths:
            origin_git_repo = None
            origin_path_tracked = None
            try:
                origin_git_repo = self.get_git_toplevel(origin_path)
            except GitError:
                pass
            else:
                self._logger.debug("")
                self._logger.debug("origin_git_repo: %s -> %s",
                                   str(origin_path), str(origin_git_repo))

                origin_path_tracked = self.is_tracked_by_git(origin_path)
                self._logger.debug("origin_is_tracked: %s -> %s",
                                   str(origin_path), str(origin_path_tracked))

            if origin_path_tracked and origin_git_repo == self._dest_git_repo:
                if self._cwd_git_toplevel and \
                        self._cwd_git_toplevel == origin_git_repo:
                    self._classified_source_paths["git mv"].append(origin_path)
                else:
                    self._classified_source_paths["git mv"].append(
                        origin_path.absolute()
                    )
            else:
                self._classified_source_paths["mv"].append(origin_path)

    def _step3_build_mv_commands(self):
        specify_repo = True
        if self._cwd_git_toplevel and \
                self._cwd_git_toplevel == self._dest_git_repo:
            specify_repo = False

        commands = {
            "git mv": ["git"] +
            (["-C", str(self._dest_git_repo)] if specify_repo else []) +
            ["mv", "-f"]
            if self._dest_git_repo else ["git", "mv"],

            "mv": ["mv"],
        }

        for cmd_type in ("git mv", "mv"):
            if not self._classified_source_paths[cmd_type]:
                continue

            try:
                self._mv_commands[cmd_type]
            except KeyError:
                self._mv_commands[cmd_type] = []

            self._mv_commands[cmd_type] += commands[cmd_type]

            if self._args.verbose:
                self._mv_commands[cmd_type] += ["--verbose"]

            if self._args.force:
                self._mv_commands[cmd_type] += ["--force"]

            self._mv_commands[cmd_type] += \
                [str(item)
                 for item in self._classified_source_paths[cmd_type]]

            if cmd_type == "git mv":
                if self._cwd_git_toplevel and \
                        self._cwd_git_toplevel == self._dest_git_repo:
                    self._mv_commands[cmd_type].append(str(self._dest_path))
                else:
                    self._mv_commands[cmd_type].append(
                        str(self._dest_path.absolute())
                    )
            elif cmd_type == "mv":
                self._mv_commands[cmd_type].append(str(self._dest_path))

    def _step4_warn_too_many_files(self):
        """Display a warning before moving a large number of files/folders."""
        if self._args.warn_amount_files <= 0:
            return

        # Display
        num_files = 0
        not_displayed_files = set()
        for source_path in self._source_paths:
            if num_files >= self._args.warn_amount_files:
                for cur_path in not_displayed_files:
                    print(cur_path)
                print(source_path)
                not_displayed_files = set()
                continue

            if source_path.is_dir():
                for sub_path in source_path.glob("**/*"):
                    if not sub_path.is_dir():
                        not_displayed_files.add(str(sub_path))
                        num_files += 1
            else:
                not_displayed_files.add(str(source_path))
                num_files += 1

        # Confirm
        if num_files >= self._args.warn_amount_files:
            if not self.confirm(f"Move {num_files} files to "
                                f"'{self._dest_path}'? [y,n] "):
                sys.exit(1)

    def _step5_execute_mv_commands(self):
        if self._args.interactive:
            print("Commands:")
            for _, cmd in self._mv_commands.items():
                print("  ", subprocess.list2cmdline(cmd))

            print()
            if not self.confirm("Execute? [y,n] "):
                sys.exit(1)

        for _, cmd in self._mv_commands.items():
            print("[RUN]", subprocess.list2cmdline(cmd))
            subprocess.check_call(cmd)

    def is_tracked_by_git(self, path: os.PathLike):
        """Return True if 'path' is being tracked by Git."""
        path = Path(path)

        try:
            cmd = ["git", "-C", str(self.get_git_toplevel(path)),
                   "ls-files", "--error-unmatch", path.absolute()]
        except GitError:
            return False

        cwd = path
        if path.is_file():
            cwd = path.parent.absolute()

        try:
            subprocess.check_call(cmd,
                                  stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL,
                                  cwd=cwd,
                                  timeout=Smartmv.cmd_git_timeout)
        except subprocess.CalledProcessError:
            return False

        return True

    def get_git_toplevel(self, path: os.PathLike) -> Path:
        """Return the top-level Git directory of 'path'."""
        path = Path(path)
        err_str = \
            f"{self.exe_name}: The file is not in a Git directory: '{path}'"

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
                timeout=Smartmv.cmd_git_timeout,
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

    @staticmethod
    def confirm(prompt: str):
        while True:
            try:
                answer = input(prompt)

                if answer.lower() not in ["y", "n"]:
                    continue

                if answer.lower() == "y":
                    break

                return False
            except KeyboardInterrupt:
                print()
                sys.exit(1)

        return True


def command_line_interface():
    """Command line interface."""
    try:
        smartmv = Smartmv()
        smartmv.main()
    except subprocess.CalledProcessError as err:
        print(f"Error: {err}.", file=sys.stderr)
        sys.exit(1)
