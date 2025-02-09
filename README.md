# git-smartmv - A tool that can decide whether to use `git mv` or `mv`

The `git-smartmv` command-line tool intelligently moves files and directories by automatically selecting either `git mv` or `mv` based on the source and destination paths.

- If both the source and destination are within the same Git repository, `git-smartmv` uses `git mv`.
- If moving files between a Git repository and a non-Git directory or a different Git repository, it defaults to `mv`.

## Installation

To install *git-smartmv* executable locally in `~/.local/bin/pathaction` using [pip](https://pypi.org/project/pip/), run:
```
sudo pip install git-smartmv
```

(Omitting the `--user` flag will install *git-smartmv* system-wide in `/usr/local/bin/git-smartmv`.)

## Shell alias

To install the *git-smartmv* executable locally in `~/.local/bin/git-smartmv` using [pip](https://pypi.org/project/pip/), run:
```
alias mv="git-smartmv"
```

(Omitting the `--user` flag will install *git-smartmv* system-wide in `/usr/local/bin/git-smartmv`.)

## Usage

The `git-smartmv` command-line tool accepts similar arguments as the `mv` command, including the source file or directory to be moved, and the destination file or directory.
```
usage: git-smartmv [--option] <SOURCE>... <DEST>

options:
  -w WARNING_THRESHOLD, --warning-threshold WARNING_THRESHOLD
                        This will raise a warning if the number of files or directories being moved
                        exceeds the specified amount
  -v, --verbose         Report the names of the files and/or directories as they are being moved.
  -f, --force           Force renaming or moving of files and/or directories even if the destination
                        exists.
  -p, --non-interactive
                        Do not prompt the user to confirm before executing 'mv' and/or 'git mv'
                        commands.
```

First example:
```
git smartmv file1 file2
```

Second example:
```
git smartmv file1 dir1/ file2 file3 directory/
```

Third example (non-interactive):
```
git smartmv --non-interactive dir1/ dir2/
```

## License

Copyright (C) 2023-2025 [James Cherti](https://www.jamescherti.com)

Distributed under terms of the GNU General Public License version 3.

## Links

- [Git-smartmv @PyPI](https://pypi.org/project/git-smartmv/)
- [Git-smartmv @GitHub](https://github.com/jamescherti/git-smartmv/)
