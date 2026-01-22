# GitHub Setup Guide

Your project has been initialized with Git and is ready to push to GitHub.

## Steps to Push to GitHub

### 1. Create a New Repository on GitHub

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon in the top right corner
3. Select **"New repository"**
4. Fill in the details:
   - **Repository name**: `crowd-risk-monitoring` (or your preferred name)
   - **Description**: "Live crowd risk monitoring platform with real-time CCTV analysis"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click **"Create repository"**

### 2. Connect Your Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these commands in your terminal:

```bash
# Add the remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/crowd-risk-monitoring.git

# Or if you prefer SSH:
# git remote add origin git@github.com:YOUR_USERNAME/crowd-risk-monitoring.git

# Push your code to GitHub
git branch -M main
git push -u origin main
```

### 3. Alternative: Using GitHub CLI (if installed)

If you have GitHub CLI installed, you can create and push in one command:

```bash
gh repo create crowd-risk-monitoring --public --source=. --remote=origin --push
```

## What's Already Committed

✅ All source code files
✅ Configuration files
✅ Documentation (README, QUICKSTART, SYSTEM_EXPLANATION)
✅ Requirements file
✅ .gitignore (excludes data files, logs, videos)

## Files Excluded (via .gitignore)

- Video files (*.mp4, *.avi)
- Generated data files
- Log files
- Python cache files
- IDE configuration files

## Next Steps After Pushing

1. Add a repository description on GitHub
2. Add topics/tags: `crowd-monitoring`, `opencv`, `fastapi`, `streamlit`, `computer-vision`, `risk-analysis`
3. Consider adding a LICENSE file
4. Enable GitHub Actions for CI/CD (optional)
5. Add collaborators if working in a team

## Useful Git Commands

```bash
# Check status
git status

# Add new files
git add .

# Commit changes
git commit -m "Your commit message"

# Push to GitHub
git push

# Pull latest changes
git pull

# View commit history
git log
```
