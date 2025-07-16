# Git Unreachable Objects Scraper

This repository contains two scripts, `git_garbage_scraper.sh` (Bash) and `git_garbage_scraper.py` (Python), designed to detect and display details about unreachable or dangling Git objects (specifically commits) in a Git repository. These scripts help identify commits that are no longer referenced by any branch, tag, or reflog, and provide detailed information such as commit metadata, diffs from parent commits, and associated file contents.

## Files

### 1. `git_garbage_scraper.sh`

#### Features
- Detects unreachable or dangling commits
- Displays commit metadata
- Shows the diff between the commit and its parent, if applicable
- Lists all files in the commit's tree and their blob SHAs
- Optionally displays the content of each file with the `-c` or `--content` flag
- Recursively traverses the commit's tree to list all files

#### Usage
```bash
./git_garbage_scraper.sh [repository_path] [-c | --content]
```
- `repository_path`: Path to the Git repository (defaults to the current directory `.`).
- `-c | --content`: Optional flag to display the content of each file (blob) in the commit's tree.

#### Example
```bash
# Scan the repository in the working directory
./git_garbage_scraper.sh

# Scan a specific repository
./git_garbage_scraper.sh /path/to/repo

# Scan and display file contents
./git_garbage_scraper.sh /path/to/repo --content
```

#### Output
- If no unreachable objects are found:
  ```
  No unreachable Git objects found.
  ```
- For each unreachable commit:
  - Commit SHA and metadata (author, date, message).
  - Diff from the parent commit (if available).
  - List of files in the commit's tree with their blob SHAs.
  - File contents (if `--content` is specified).

### 2. `git_garbage_scraper.py`
A script that performs the same functionality as the Bash script, but implemented using Python

#### Features
- Similar to the Bash script, it detects unreachable or dangling commits
- Displays commit metadata, diffs from parent commits, and lists files in the commit's tree.
- Optionally shows file contents with the `-c` or `--content` flag.
- Increased error handling compared to the Bash script

#### Requirements
- Python 3.x
- Git installed and accessible from the command line.

#### Usage
```bash
python3 git_garbage_scraper.py [repository_path] [-c | --content]
```
- `repository_path`: Path to the Git repository (defaults to the current directory `.`).
- `-c | --content`: Optional flag to display the content of each file (blob) in the commit's tree.

#### Example
```bash
# Scan the repository in the working directory
python3 git_garbage_scraper.py

# Scan a specific repository
python3 git_garbage_scraper.py /path/to/repo

# Scan and display file contents
python3 git_garbage_scraper.py /path/to/repo --content
```

#### Output
- Similar to the Bash script, it outputs:
  - A message if no unreachable objects are found.
  - For each unreachable commit: metadata, diff from parent (if available), list of files with blob SHAs, and file contents (if `--content` is specified).

## Notes
- Both scripts require a valid Git repository at the specified path.
- Use the `--content` flag with caution, as it can produce large output if the commit contains many or large files.
- Ensure you have sufficient permissions to access the repository and execute Git commands.