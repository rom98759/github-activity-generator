### GitHub Activity Generator
A script to instantly generate a beautiful GitHub Contributions Graph for the last year.

## Table of Contents
- [Disclaimer](#-disclaimer)
- [How to use](#how-to-use)
- [How it works](#how-it-works)
- [What's New in this Fork](#whats-new-in-this-fork)
- [Troubleshooting](#troubleshooting)

## ⚠ Disclaimer
This script is a fork of [Shpota's GitHub Activity Generator](https://github.com/Shpota/github-activity-generator). I am not the original author and am not responsible for misuse. The goal is not to cheat but to create a visually appealing contributions graph if people judge your GitHub activity.

## What it looks like
### Before:
![Before](before.png)
### After:
![After](after.png)

## How to use
1. Create an empty **SPAM** GitHub repository or use an existing one (Not recommended).
2. Download [contribute.py](https://github.com/rom98759/github-activity-generator/archive/refs/heads/main.zip) and run it:
```sh
python contribute.py --repository=git@github.com:user/repo.git
```
After running, it may take a few minutes for GitHub to reindex your activity.

## How it works
The script initializes a git repo, generates commits (0-20 per day) for the last year, and then pushes the changes to a remote repository.

## Customizations
Try `python contribute.py --help` for more options.

You can adjust commit frequency, the number of commits per day, and more. For example, to make 1-12 commits per day, 60% of the year:
```sh
python contribute.py --max_commits=12 --frequency=60 --repository=git@github.com:user/repo.git
```
To exclude weekends:
```sh
python contribute.py --no_weekends
```

## What's New in this Fork
Key improvements over the original:
1. **Directory Creation**: Checks if the directory exists before creating it.
2. **Git Initialization**: Initializes Git and checks/creates the `main` branch if needed.
3. **User Configuration**: Sets Git user config after branch creation and remote verification.
4. **Remote Check**: Verifies if the remote exists before adding.
5. **Branch Management**: Ensures `main` exists before using it.
6. **Commit Handling**: Adds only the `README.md` file for commits.
7. **Push to Remote**: Merges with the remote before pushing.
8. **Error Handling**: Adds additional checks (e.g., `has_changes()` and `check_git_status()`).
9. **Modularity**: More functions for handling various tasks like remote, branch, and status checks.

## System Requirements
Ensure Python and Git are installed.

## Troubleshooting
- **No Activity Reflected**: Wait for GitHub to reindex your activity (can take a few minutes).
- **Private Repository**: Enable showing private contributions [here](https://help.github.com/en/articles/publicizing-or-hiding-your-private-contributions-on-your-profile).
- **Email Mismatch**: Ensure your GitHub email matches your local Git email:
```sh
git config --get user.email
git config --global user.email "user@example.com"
```
