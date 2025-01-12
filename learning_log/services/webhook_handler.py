from github import Github, Auth
from datetime import datetime
from ..models import LearningLog

class CommitExtractor:
    def __init__(self, github_token):
        self.github = Github(auth=Auth.Token(github_token))
    
    def fetch_commits(self, username=None, since=None):
        """Fetch commits from GitHub"""
        # Move existing fetch_github_commits logic here
        
    def process_commit(self, commit_data):
        """Process and store a single commit"""
        # Move existing store_learning_log logic here