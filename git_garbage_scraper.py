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

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Detect and display unreachable Git commit contents.")
    parser.add_argument("repo", nargs="?", default=".", help="Path to the Git repository")

    args = parser.parse_args()
    unreachable = get_unreachable_objects(args.repo)

    if not unreachable:
        print("No unreachable Git objects found.")
    else:
        for obj_type, sha in unreachable:
            if obj_type == "commit":
                print(f"\n=== Unreachable {obj_type} {sha} ===")
                content = get_object_content(args.repo, sha)
                print(content.strip())
