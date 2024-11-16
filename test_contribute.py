import unittest
import tempfile
import os
from subprocess import Popen, PIPE, check_output
import contribute

class TestContribute(unittest.TestCase):

	def run_command(self, commands):
		"""Execute a command and return its output."""
		result = Popen(commands, stdout=PIPE, stderr=PIPE)
		stdout, stderr = result.communicate()
		if result.returncode != 0:
			print(f"Error with command: {commands}")
			print(stderr.decode('utf-8'))
		return stdout.decode('utf-8')

	def test_arguments(self):
		"""Test the arguments passed to the script."""
		args = contribute.arguments(['-nw', '--user_name=testuser', '--user_email=testemail@example.com'])
		self.assertTrue(args.no_weekends)
		self.assertEqual(args.user_name, 'testuser')
		self.assertEqual(args.user_email, 'testemail@example.com')
		self.assertEqual(args.max_commits, 10)  # Check the default value
		self.assertTrue(1 <= contribute.contributions_per_day(args) <= 20)  # Check contributions per day

	def test_contributions_per_day(self):
		"""Test contributions per day."""
		args = contribute.arguments(['-nw'])
		self.assertTrue(1 <= contribute.contributions_per_day(args) <= 20)

	def test_commits(self):
		"""Test the number of commits created."""
		with tempfile.TemporaryDirectory() as temp_dir:
			os.chdir(temp_dir)
			# Initialize a temporary Git repository
			self.run_command(['git', 'init'])

			# Run the contribute script
			contribute.main([
				'-nw',
				'--user_name=testuser',
				'--user_email=testemail@example.com',
				'-mc=5',  # Max number of commits
				'-fr=5',  # Number of contributions per weekday
				'-db=1',  # Number of commits per day during weekdays
				'-da=1'   # Number of commits per day during weekends
			])

			# Check the number of commits in the repository
			commit_count = int(self.run_command(['git', 'rev-list', '--count', 'HEAD']))
			self.assertGreater(commit_count, 0)

			# Check commit messages
			commits = self.run_command(['git', 'log', '--pretty=%B']).split('\n')
			for commit in commits:
				if commit:  # Ignore empty lines
					self.assertTrue(commit.startswith('Contribution:'))  # Commit message starts with 'Contribution:'

	def test_invalid_commits(self):
		"""Test an invalid number of commits."""
		with tempfile.TemporaryDirectory() as temp_dir:
			os.chdir(temp_dir)
			# Initialize a temporary Git repository
			self.run_command(['git', 'init'])

			# Run the script with an invalid number of commits (too high)
			contribute.main([
				'-nw',
				'--user_name=testuser',
				'--user_email=testemail@example.com',
				'-mc=100',  # Max number of commits too high
				'-fr=50',   # Number of contributions per day too high
				'-db=100',  # Number of commits per day too high
				'-da=100'   # Number of commits per day too high
			])

			# Check that the number of commits does not exceed a certain limit
			commit_count = int(self.run_command(['git', 'rev-list', '--count', 'HEAD']))
			self.assertLessEqual(commit_count, 20 * 10)  # Commit limit (20 days * 10 max contributions)

if __name__ == '__main__':
	unittest.main()
