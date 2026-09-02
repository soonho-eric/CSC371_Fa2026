## Bash Terminal Cheat Sheet

Use these when working on a terminal (Mac or Linux), git bash and miniforge shell (Windows).

## Navigation

| Command     | Description                      |
| ----------- | -------------------------------- |
| `pwd`       | Show your current directory      |
| `ls`        | List files and folders           |
| `ls -l`     | List files with more details     |
| `ls -a`     | Include hidden files             |
| `cd folder` | Move into a folder               |
| `cd /full/dir/addr` | Move into a folder               |
| `cd ..`     | Move up one directory            |
| `cd ~`      | Move to your home directory      |

Useful shortcuts:

* `Tab` — autocomplete commands and filenames
* `↑` / `↓` — move through command history
* `Ctrl+C` — stop a running command
* `Ctrl+L` — clear the terminal

---

## Files and Folders

| Command                 | Description                           |
| ----------------------- | ------------------------------------- |
| `mkdir folder`          | Create a new folder                   |
| `touch file.txt`        | Create an empty file                  |
| `cp file1 file2`        | Copy a file                           |
| `cp -r folder1 folder2` | Copy a folder                         |
| `mv file destination/`  | Move a file                           |
| `mv old new`            | Rename a file or folder               |
| `rm file`               | Delete a file                         |
| `rm -r folder`          | Delete a folder and its contents      |
| `cat file.txt`          | Display the contents of a file        |
| `less file.txt`         | View a long file one screen at a time |
| `nano file.txt`         | Edit a text file in the terminal      |

Be careful with `rm`: deleted files usually cannot be recovered.

Paths you will commonly see:

| Symbol | Meaning                                        |
| ------ | ---------------------------------------------- |
| `.`    | Current directory                              |
| `..`   | Parent directory                               |
| `~`    | Home directory                                 |
| `/`    | Root directory / beginning of an absolute path |

For filenames containing spaces, use quotes:

```bash
cd "My Documents"
```

---

## Git

| Command                   | Description                                        |
| ------------------------- | -------------------------------------------------- |
| `git clone URL`           | Download a repository for the first time           |
| `git status`              | Show changed, staged, and untracked files          |
| `git pull`                | Download and merge new changes from GitHub         |
| `git add file`            | Stage a file for the next commit                   |
| `git add .`               | Stage all current changes                          |
| `git commit -m "message"` | Save staged changes as a commit                    |
| `git push`                | Upload your commits to GitHub                      |
| `git log --oneline`       | Show recent commits                                |
| `git remote -v`           | Show the GitHub URL associated with the repository |

A typical Git workflow is:

```bash
git pull
git status
git add .
git commit -m "Journal 1"
git push
```

With this repository as an example, cloning using ssh looks like

```bash
git clone git@github.com:soonho-eric/CSC371_Fa2026.git
cd repository
```
or using HTTPS,

```bash
git clone https://github.com/soonho-eric/CSC371_Fa2026.git
cd repository
```
