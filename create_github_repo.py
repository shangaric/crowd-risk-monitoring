"""
Script to create GitHub repository and push code
"""
import requests
import subprocess
import sys
import os

# GitHub username
USERNAME = "shangaric"
REPO_NAME = "crowd-risk-monitoring"
DESCRIPTION = "Live crowd risk monitoring platform with real-time CCTV analysis and ML-based hazard detection"

def create_repo_with_api():
    """Create repository using GitHub API"""
    print("Creating GitHub repository...")
    print(f"Repository: {USERNAME}/{REPO_NAME}")
    
    # Check for GitHub token
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("\n[!] GitHub token not found in environment.")
        print("To create the repository automatically, you need a GitHub Personal Access Token.")
        print("\nOption 1: Create token and set it:")
        print("  1. Go to: https://github.com/settings/tokens")
        print("  2. Generate new token (classic) with 'repo' scope")
        print("  3. Run: $env:GITHUB_TOKEN='your_token_here'")
        print("  4. Then run this script again")
        print("\nOption 2: Create repository manually:")
        print(f"  1. Go to: https://github.com/new")
        print(f"  2. Name: {REPO_NAME}")
        print(f"  3. Description: {DESCRIPTION}")
        print("  4. Don't initialize with README")
        print("  5. Click 'Create repository'")
        print("  6. Then run: git push -u origin main")
        return False
    
    # Create repository via API
    url = f"https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": REPO_NAME,
        "description": DESCRIPTION,
        "private": False,
        "auto_init": False
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 201:
            print(f"[SUCCESS] Repository created successfully!")
            print(f"   URL: https://github.com/{USERNAME}/{REPO_NAME}")
            return True
        elif response.status_code == 422:
            print("[INFO] Repository might already exist or name is invalid")
            # Try to push anyway
            return True
        else:
            print(f"[ERROR] Error creating repository: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

def push_to_github():
    """Push code to GitHub"""
    print("\nPushing code to GitHub...")
    try:
        result = subprocess.run(
            ["git", "push", "-u", "origin", "main"],
            capture_output=True,
            text=True,
            check=True
        )
        print("[SUCCESS] Code pushed successfully!")
        print(f"   View at: https://github.com/{USERNAME}/{REPO_NAME}")
        return True
    except subprocess.CalledProcessError as e:
        if "not found" in e.stderr:
            print("[ERROR] Repository not found on GitHub.")
            print("   Please create it first (see instructions above)")
        else:
            print(f"[ERROR] Error pushing: {e.stderr}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("GitHub Repository Setup")
    print("=" * 60)
    
    # Try to create repository
    repo_exists = create_repo_with_api()
    
    # Push code
    if repo_exists:
        push_to_github()
    else:
        print("\n" + "=" * 60)
        print("Manual Setup Required")
        print("=" * 60)
        print("\nAfter creating the repository on GitHub, run:")
        print("  git push -u origin main")
