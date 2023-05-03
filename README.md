# git-smartmv - A tool that can decide whether to use `git mv` or `mv`

The `git-smartmv` is a command-line tool, written by
[James Cherti](https://www.jamescherti.com), for moving files and
directories without having to worry about manually choosing whether to use
`git mv` or `mv`.

The `git-smartmv` tool determines whether to use `git mv` or `mv` based on the
source and the destination path:
- If the file or directory is being moved within a Git repository,
  `git-smartmv` uses `git mv`.
- If the file is being moved between a Git repository and a non-Git directory
  or a different Git repository, `git-smartmv` uses `mv`.

## Installation

```
sudo pip install git-smartmv
```

## Shell alias

It is recommended to add the following alias to `~/.bashrc`:
```
alias mv="git-smartmv"
```

## Usage

The `git-smartmv` command-line tool accepts the same arguments as the `mv`
command, including the source file or directory to be moved, and the
destination file or directory.
```usage: git-smartmv [--option] <SOURCE>... <DEST>

A command-line tool that can decide whether to use `git mv` or `mv`.

positional arguments:
  args                  Files and/or directories

options:
  -h, --help            show this help message and exit
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
git smartmv file1 dir1/ file2 file3 directory/
```

Second example:
```
git smartmv file1 file2
```

Third example (non-interactive):
```
git smartmv -f dir1/ dir2/
```

## License

Distributed under terms of the GNU General Public License version 3.

## Links

- [Git-smartmv @PyPI](https://pypi.org/project/git-smartmv/)
- [Git-smartmv @GitHub](https://github.com/jamescherti/git-smartmv/)
