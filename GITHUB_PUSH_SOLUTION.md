# GitHub Push Solution

## The Problem

You're unable to push your code to GitHub because the repository history contains large files in the `.venv` folder that exceed GitHub's file size limits:

- `.venv/lib/python3.11/site-packages/pyarrow/libarrow.1900.dylib` (50.88 MB)
- `.venv/lib/python3.11/site-packages/torch/lib/libtorch_cpu.dylib` (161.15 MB)

GitHub has the following limits:

- Recommended maximum file size: 50 MB
- Hard limit: 100 MB

## Solution Options

I've provided two scripts to help resolve this issue:

### Option 1: Fresh Start (Recommended for Beginners)

This creates a completely new Git repository, effectively removing all history:

```bash
./fresh_start.sh
```

**Pros:**

- Simple and straightforward
- Guaranteed to work
- No additional tools needed

**Cons:**

- Loses all Git history
- Requires creating a new remote repository

After running the script:

1. Create a new repository on GitHub (without initializing it)
2. Connect your local repository to the new GitHub repository:
   ```bash
   git remote add origin https://github.com/yourusername/your-new-repo.git
   git push -u origin main
   ```

### Option 2: Clean History with BFG (Advanced)

This uses the BFG Repo-Cleaner to remove large files from history:

```bash
./clean_repo.sh
```

**Pros:**

- Preserves Git history (except for the removed files)
- Can keep the same remote repository

**Cons:**

- Requires installing additional tools
- More complex
- May still have issues with very large repositories

## Preventing Future Issues

To prevent this issue in the future:

1. **Never commit virtual environments**: Always ensure `.venv`, `venv`, or similar directories are in your `.gitignore` before your first commit.

2. **Use Git LFS for large files**: If you need to track large files, use Git Large File Storage:

   ```bash
   brew install git-lfs
   git lfs install
   git lfs track "*.large_extension"
   ```

3. **Check file sizes before committing**: Use this command to find large files:

   ```bash
   find . -type f -size +50M | grep -v ".git/" | sort -rh
   ```

4. **Set up Git hooks**: Consider setting up a pre-commit hook to prevent large files from being committed.

## Additional Resources

- [GitHub documentation on large files](https://docs.github.com/en/repositories/working-with-files/managing-large-files)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
- [Git LFS documentation](https://git-lfs.github.com/)

Remember: Always make a backup before performing major operations on your Git repository!
