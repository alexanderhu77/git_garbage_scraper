#!/bin/bash

REPO_PATH="${1:-.}"
SHOW_CONTENT=0

if [[ "$2" == "-c" || "$2" == "--content" ]]; then
    SHOW_CONTENT=1
fi

cd "$REPO_PATH" || { echo "Invalid repo path: $REPO_PATH"; exit 1; }

UNREACHABLE=$(git fsck --full --no-reflogs | grep -E "unreachable|dangling")

if [[ -z "$UNREACHABLE" ]]; then
    echo "No unreachable Git objects found."
    exit 0
fi

while read -r line; do
    TYPE=$(echo "$line" | awk '{print $2}')
    SHA=$(echo "$line" | awk '{print $3}')

    if [[ "$TYPE" == "commit" ]]; then
        echo -e "\n=== Unreachable commit $SHA ==="
        echo "--- Commit Metadata ---"
        git cat-file -p "$SHA"

        PARENT=$(git cat-file -p "$SHA" | grep "^parent" | awk '{print $2}')
        if [[ -n "$PARENT" ]]; then
            echo -e "\n--- Diff from parent ---"
            git --no-pager diff "$PARENT" "$SHA"
        else
            echo "No parent found. Possibly an initial commit."
        fi

        TREE=$(git cat-file -p "$SHA" | grep "^tree" | awk '{print $2}')
        if [[ -z "$TREE" ]]; then
            echo "No tree found."
            continue
        fi

        echo -e "\n--- Commit Tree Files ---"
        list_blobs_recursively() {
            local tree_sha=$1
            local prefix=$2

            git ls-tree "$tree_sha" | while read -r mode type sha path; do
                full_path="$prefix$path"
                if [[ "$type" == "blob" ]]; then
                    echo "File: $full_path"
                    echo "Blob SHA: $sha"
                    if [[ $SHOW_CONTENT -eq 1 ]]; then
                        echo "--- Blob Content ---"
                        git cat-file -p "$sha"
                    fi
                elif [[ "$type" == "tree" ]]; then
                    list_blobs_recursively "$sha" "$full_path/"
                fi
            done
        }

        list_blobs_recursively "$TREE" ""
    fi
done <<< "$UNREACHABLE"