#!/bin/bash

echo "=== Song Mashup Fresh Start ==="
echo "This script will help you create a new, clean Git repository for your project."
echo ""

# Create backup
echo "=== Step 1: Creating a backup of your current code ==="
mkdir -p ../song-mashup-backup
cp -R * ../song-mashup-backup/
echo "Backup created at: ../song-mashup-backup"
echo ""

# Remove .git directory
echo "=== Step 2: Removing old Git history ==="
rm -rf .git
echo ""

# Initialize new repository
echo "=== Step 3: Creating a new Git repository ==="
git init
echo ""

# Add all files respecting .gitignore
echo "=== Step 4: Adding files to the new repository ==="
git add .
git status
echo ""

echo "=== Step 5: Creating first commit ==="
git commit -m "Initial commit with clean history"
echo ""

echo "=== Fresh Start Complete ==="
echo ""
echo "Now you need to set up a new remote repository. If you want to use GitHub:"
echo "1. Create a new repository on GitHub (without any files)"
echo "2. Run the following commands:"
echo "   git remote add origin https://github.com/yourusername/your-new-repo.git"
echo "   git push -u origin main"
echo ""
echo "Your code is now in a clean repository without the .venv folder in history." 