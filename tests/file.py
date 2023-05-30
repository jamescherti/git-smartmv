#!/usr/bin/env python

import os
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from git_smartmv.file import File


def test_file():
    with TemporaryDirectory("test_smartmv") as tmpdir:
        git_dir = Path(tmpdir).joinpath("repo")
        os.makedirs(git_dir)
        try:
            file_path = git_dir.joinpath("file")
            with open(file_path, "w",
                      encoding="utf-8") as fhandler:
                fhandler.write("Hello world")
            subprocess.check_call(["git", "init"], cwd=git_dir)

            file_class = File(str(file_path))
            assert file_class.path.resolve() == file_path.resolve()
            assert file_class.git_toplevel().resolve() == git_dir.resolve()

            assert file_class.is_tracked_by_git() == False
            subprocess.check_call(["git", "add", "file"], cwd=git_dir)
            assert file_class.is_tracked_by_git() == True
        finally:
            shutil.rmtree(git_dir)
