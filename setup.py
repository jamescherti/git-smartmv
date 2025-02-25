#!/usr/bin/env python
"""A setuptools based setup module."""

from setuptools import setup, find_packages
from pathlib import Path

CURRENT_DIRECTORY = Path(__file__).parent.resolve()
LONG_DESCRIPTION = \
    (CURRENT_DIRECTORY / "README.md").read_text(encoding="utf-8")

setup(
    name="git-smartmv",
    version="1.0.5",
    packages=find_packages(),
    description=("A command-line tool that can decide whether to "
                 "use `git mv` or `mv`."),
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/jamescherti/git-smartmv",
    author="James Cherti",
    python_requires=">=3.6, <4",
    install_requires=[],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Environment :: Console",
        "Operating System :: POSIX :: Linux",
        "Operating System :: POSIX :: Other",
        "Operating System :: Unix",
        "Programming Language :: Unix Shell",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: System :: Filesystems",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
    ],
    entry_points={
        "console_scripts": [
            "git-smartmv=git_smartmv.__init__:command_line_interface",
        ],
    },
)
