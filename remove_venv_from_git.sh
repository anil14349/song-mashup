#!/bin/bash

# Step 1: Remove .venv from git cache
git rm -r --cached .venv

# Step 2: Create a new commit that removes these files from git tracking
git commit -m "Remove .venv folder from git tracking"

# Step 3: Check git status
git status

echo ""
echo "The .venv folder has been removed from git tracking (but still exists on your local machine)."
echo "Now you can try pushing with: git push origin main"
echo ""
echo "If you still have issues, you may need to use git filter-branch or BFG Repo-Cleaner"
echo "to completely remove the large files from your git history." 