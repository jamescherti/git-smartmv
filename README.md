# Git-smartmv - A tool that can decide whether to use `git mv` or `mv`

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

## Bash Shell Alias

It is recommended to add the following alias to `~/.bashrc`:
```
alias mv="git-smartmv"
```

## Usage

The `git-smartmv` command-line tool accepts the same arguments as the `mv`
command, including the source file or directory to be moved, and the
destination file or directory.

First example:
```
git smartmv file1 dir1/ file2 file3 directory/
```

Second example:
```
git smartmv file1 file2
```

Third example:
```
git smartmv dir1/ dir2/
```

## License

Distributed under terms of the GNU General Public License version 3.

## Links

- [Git-smartmv @PyPI](https://pypi.org/project/git-smartmv/)
- [Git-smartmv @GitHub](https://github.com/jamescherti/git-smartmv/)
