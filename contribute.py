#!/usr/bin/env python
import argparse
import os
import sys
from datetime import datetime, timedelta
from random import randint
from subprocess import Popen, PIPE

def main(def_args=sys.argv[1:]):
	"""
	Main function to generate GitHub activity by creating a repository and making commits.
	Args:
		def_args (list): List of command-line arguments passed to the script.
	"""

	# 1. Parse command-line arguments
	args = arguments(def_args)

	# 2. Determine the current date and time
	curr_date = datetime.now()
	directory = 'repository-' + curr_date.strftime('%Y-%m-%d-%H-%M-%S')

	# Set repository name and user details
	repository = args.repository
	user_name = args.user_name
	user_email = args.user_email

	# If repository is provided, derive directory name
	if repository is not None:
		start = repository.rfind('/') + 1
		end = repository.rfind('.')
		directory = repository[start:end]

	# Get additional configuration
	no_weekends = args.no_weekends
	frequency = args.frequency
	days_before = args.days_before
	if days_before < 0:
		sys.exit('days_before must not be negative')

	days_after = args.days_after
	if days_after < 0:
		sys.exit('days_after must not be negative')

	# 3. Create repository directory
	if not os.path.exists(directory):
		os.mkdir(directory)
	else:
		print(f"The directory {directory} already exists. Using this directory.")

	os.chdir(directory)

	# 4. Initialize Git repository
	run(['git', 'init'])

	# 5. Check if remote repository exists and set up if necessary
	remote_exists = check_remote_exists()
	if not remote_exists and repository is not None:
		run(['git', 'remote', 'add', 'origin', repository])

	# 6. Check if 'main' branch exists and create it if necessary
	branch_exists = check_branch_exists("main")
	if not branch_exists:
		run(['git', 'checkout', '-b', 'main'])

	# 7. Configure Git user details
	if user_name is not None:
		run(['git', 'config', 'user.name', user_name])

	if user_email is not None:
		run(['git', 'config', 'user.email', user_email])

	# 8. Set the start date for commits
	start_date = curr_date.replace(hour=20, minute=0) - timedelta(days_before)

	# 9. Generate commits based on specified frequency and date range
	for day in (start_date + timedelta(n) for n in range(days_before + days_after)):
		if (not no_weekends or day.weekday() < 5) and randint(0, 100) < frequency:
			for commit_time in (day + timedelta(minutes=m) for m in range(contributions_per_day(args))):
				contribute(commit_time)

	# 10. Push changes to the remote repository if specified
	if repository is not None:
		print('Pushing changes to the remote repository...')
		run(['git', 'fetch', 'origin'])
		run(['git', 'merge', 'origin/main', '--allow-unrelated-histories', '--strategy=recursive', '--strategy-option=theirs', '--no-edit'])
		run(['git', 'push', '-u', 'origin', 'main'])

	# 11. Print success message
	print('\nRepository generation ' +
		  '\x1b[6;30;42mcompleted successfully\x1b[0m!')


def check_remote_exists():
	"""
	Check if a Git branch with the specified name exists in the current repository.
	Returns:
		bool: True if the branch exists, False otherwise or if an error occurs
	"""
	try:
		result = Popen(['git', 'remote', 'get-url', 'origin'], stdout=PIPE, stderr=PIPE)
		result.communicate()
		return result.returncode == 0
	except Exception:
		return False

def check_branch_exists(branch_name):
	"""
	Check if a Git branch with the specified name exists in the current repository.
	Args:
		branch_name (str): The name of the branch to check.
	Returns:
		bool: True if the branch exists, False otherwise or if an error occurs
	"""
	try:
		result = Popen(['git', 'rev-parse', '--verify', branch_name], stdout=PIPE, stderr=PIPE)
		result.communicate()
		return result.returncode == 0
	except Exception:
		return False

def run(commands):
	Popen(commands).wait()

def contribute(date):
	"""
	Create a new file and commit it to the Git repository.
	Args:
		date (datetime): The date and time for the commit.
	"""
	with open('README.md', 'a') as file:
		file.write(message(date) + '\n\n')

	run(['git', 'add', 'README.md'])

	if has_changes():
		run(['git', 'commit', '-m', '"%s"' % message(date),
			 '--date', date.strftime('"%Y-%m-%d %H:%M:%S"')])

def has_changes():
	"""
	Check if there are any changes in the Git repository.
	Returns:
		bool: True if there are changes, False otherwise
	"""
	status = Popen(['git', 'status', '--porcelain'], stdout=PIPE).communicate()[0].decode('utf-8')
	return bool(status.strip())

def check_git_status():
	"""
	Check if there are any uncommitted changes in the Git repository.
	If there are changes, print an error message and exit the script.
	"""
	status = Popen(['git', 'status', '--porcelain'], stdout=PIPE).communicate()[0].decode('utf-8')
	if status:
		print('Files are modified or untracked, please commit them before continuing.')
		sys.exit(1)

def check_branch():
	"""
	Check if the current branch is 'main'.
	If the current branch is 'HEAD', create a new 'main' branch.
	If the current branch is not 'main', print an error message and exit the script.
	"""
	current_branch = Popen(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=PIPE).communicate()[0].decode('utf-8').strip()
	if current_branch == 'HEAD':
		run(['git', 'checkout', '-b', 'main'])
	elif current_branch != 'main':
		print(f'You are currently on branch {current_branch}, please switch to the "main" branch.')
		sys.exit(1)

def message(date):
	"""
	Generate a commit message based on the specified date.
	Args:
		date (datetime): The date and time for the commit.
	Returns:
		str: The commit message with the formatted date.
	"""
	return date.strftime('Contribution: %Y-%m-%d %H:%M')

def contributions_per_day(args):
	"""
	Determine the number of commits to make on a given day.
	Args:
		args (argparse.Namespace): Parsed command-line arguments.
	Returns:
		int: The number of commits to make on a given day.
	"""
	max_c = args.max_commits
	if max_c > 20:
		max_c = 20
	if max_c < 1:
		max_c = 1
	return randint(1, max_c)

def arguments(argsval):
	"""
	Parses command-line arguments for the script.
	Returns:
		argparse.Namespace: Parsed command-line arguments.
	"""
	parser = argparse.ArgumentParser()
	parser.add_argument('-nw', '--no_weekends',
						required=False, action='store_true', default=False,
						help="""do not commit on weekends""")
	parser.add_argument('-mc', '--max_commits', type=int, default=10,
						required=False, help="""Defines the maximum amount of
						commits a day the script can make. Accepts a number
						from 1 to 20. If N is specified the script commits
						from 1 to N times a day. The exact number of commits
						is defined randomly for each day. The default value
						is 10.""")
	parser.add_argument('-fr', '--frequency', type=int, default=80,
						required=False, help="""Percentage of days when the
						script performs commits. If N is specified, the script
						will commit N%% of days in a year. The default value
						is 80.""")
	parser.add_argument('-r', '--repository', type=str, required=False,
						help="""A link on an empty non-initialized remote git
						repository. If specified, the script pushes the changes
						to the repository. The link is accepted in SSH or HTTPS
						format. For example: git@github.com:user/repo.git or
						https://github.com/user/repo.git""")
	parser.add_argument('-un', '--user_name', type=str, required=False,
						help="""Overrides user.name git config.
						If not specified, the global config is used.""")
	parser.add_argument('-ue', '--user_email', type=str, required=False,
						help="""Overrides user.email git config.
						If not specified, the global config is used.""")
	parser.add_argument('-db', '--days_before', type=int, default=365,
						required=False, help="""Specifies the number of days
						before the current date when the script will start
						adding commits. For example: if it is set to 30 the
						first commit date will be the current date minus 30
						days.""")
	parser.add_argument('-da', '--days_after', type=int, default=0,
						required=False, help="""Specifies the number of days
						after the current date until which the script will be
						adding commits. For example: if it is set to 30 the
						last commit will be on a future date which is the
						current date plus 30 days.""")
	return parser.parse_args(argsval)

if __name__ == "__main__":
	main()
