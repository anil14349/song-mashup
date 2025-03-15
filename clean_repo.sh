#!/bin/bash

echo "=== Song Mashup Git Repository Cleaner ==="
echo "This script will help clean up your Git repository by removing the .venv folder from history."
echo ""

# Check if BFG is installed
if ! command -v bfg &> /dev/null; then
    echo "BFG Repo-Cleaner is not installed. Installing via Homebrew..."
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "Homebrew is not installed. Please install Homebrew first:"
        echo "Visit: https://brew.sh/"
        exit 1
    fi
    
    # Install BFG
    brew install bfg
fi

echo "=== Step 1: Creating a fresh clone of your repository ==="
echo "This is required for BFG to work correctly."

# Create a backup directory
mkdir -p ../song-mashup-backup
cp -R * ../song-mashup-backup/

# Create a temp directory for the clean repo
mkdir -p ../song-mashup-clean
cd ..

# Clone the repository
echo "=== Step 2: Cleaning the repository with BFG ==="
cd song-mashup
git gc

# Create a text file with directories/files to remove
cat > ../delete-folders.txt << EOL
.venv
EOL

# Run BFG to remove the specified directories from history
bfg --delete-folders .venv --no-blob-protection

# Clean up the repo
echo "=== Step 3: Cleaning up and finalizing changes ==="
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo ""
echo "=== Repository Cleaning Complete ==="
echo ""
echo "Your repository should now be clean of the .venv directory."
echo "Try pushing with: git push -f origin main"
echo ""
echo "If you still have issues, you may need to create a completely new repository and push your code there."
echo "A backup of your files has been created in: ../song-mashup-backup" 