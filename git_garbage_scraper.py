import subprocess

def get_unreachable_objects(repo_path="."):
    '''
    Find unreachable Git objects using fsck.
    ''' 

    try:
        result = subprocess.run(
            ["git", "fsck", "--full", "--no-reflogs"],
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        unreachable_objects = []
        for line in result.stdout.splitlines():
            if line.startswith("unreachable") or line.startswith("dangling"):
                parts = line.strip().split()
                if len(parts) >= 3:
                    obj_type = parts[1]
                    sha = parts[2]
                    unreachable_objects.append((obj_type, sha))

        return unreachable_objects

    except subprocess.CalledProcessError as e:
        print("Error running git fsck:", e.stderr)
        return []

def get_object_content(repo_path, sha):
    '''
    Get the raw content of a Git object using git cat-file -p.
    
    '''

    try:
        result = subprocess.run(
            ["git", "cat-file", "-p", sha],
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error reading object {sha}: {e.stderr}"


def get_commit_parent(repo_path, commit_sha):
    '''
    Get the parent commit SHA of a given commit.
    '''

    content = get_object_content(repo_path, commit_sha)
    for line in content.splitlines():
        if line.startswith("parent "):
            return line.split()[1]
    return None

def get_commit_tree_sha(repo_path, commit_sha):
    '''
    Extract the tree SHA from a commit object.
    '''
    content = get_object_content(repo_path, commit_sha)
    for line in content.splitlines():
        if line.startswith("tree "):
            return line.split()[1]
    return None

def get_diff_between_commits(repo_path, parent_sha, child_sha):
    '''
    Get the diff between two commits.
    '''
    
    try:
        result = subprocess.run(
            ["git", "diff", parent_sha, child_sha],
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error running diff: {e.stderr}"

def get_blobs_from_tree(repo_path, tree_sha, prefix=""):
    '''
    Recursively get all blobs and their paths from a tree SHA.
    '''
    blobs = []
    try:
        result = subprocess.run(
            ["git", "ls-tree", tree_sha],
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        for line in result.stdout.splitlines():
            parts = line.split(None, 4)
            if len(parts) >= 4:
                mode, type_, sha, path = parts[0], parts[1], parts[2], parts[3]
                full_path = f"{prefix}/{path}".lstrip("/")
                if type_ == "blob":
                    blobs.append((full_path, sha))
                elif type_ == "tree":
                    blobs.extend(get_blobs_from_tree(repo_path, sha, full_path))
        return blobs
    except subprocess.CalledProcessError as e:
        print(f"Error reading tree {tree_sha}: {e.stderr}")
        return []


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Detect and display unreachable Git commit contents.")
    parser.add_argument("repo", nargs="?", default=".", help="Path to the Git repository")
    parser.add_argument("-c", "--content", action="store_true", help="Display content of unreachable files")

    args = parser.parse_args()
    unreachable = get_unreachable_objects(args.repo)

    if not unreachable:
        print("No unreachable Git objects found.")
    else:
        for obj_type, sha in unreachable:
            if obj_type == "commit":
                print(f"\n=== Unreachable commit {sha} ===")
                print("--- Commit Metadata ---")
                commit_content = get_object_content(args.repo, sha)
                print(commit_content.strip())

                parent_sha = get_commit_parent(args.repo, sha)
                if parent_sha:
                    print("\n--- Diff from parent ---")
                    diff_output = get_diff_between_commits(args.repo, parent_sha, sha)
                    print(diff_output.strip())
                else:
                    print("No parent found. Possibly an initial commit.")

                print("\n--- Commit Tree Files ---")
                tree_sha = get_commit_tree_sha(args.repo, sha)
                if not tree_sha:
                    print("No tree found.")
                    continue

                blobs = get_blobs_from_tree(args.repo, tree_sha)
                for file_path, blob_sha in blobs:
                    print(f"File: {file_path}\nBlob SHA: {blob_sha}")
                    if args.content:
                        content_display = get_object_content(args.repo, blob_sha)
                        print(content_display.strip())

