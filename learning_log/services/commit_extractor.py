''' STAGE 1: COMMIT EXTRACTION AND STORAGE '''

from github import Github, Auth
from datetime import datetime
from ..models import LearningLog
import os
from flask import jsonify
import logging

logger = logging.getLogger(__name__)

class CommitExtractor:
    def __init__(self, github_token):
        # store token in instance to avoid reading env multiple times
        self.github_token = github_token
        self.github = Github(auth=Auth.Token(github_token))
    
    def fetch_github_commits(self, username=None, since=None):
        """Fetch commits from GitHub"""
        # use instance github client instead of creating new one
        user = self.github.get_user(username) if username else self.github.get_user()
        
        commits_data = []
        for repo in user.get_repos():
            for commit in repo.get_commits(author=user.login):
                file_changes = [{
                    'filename': f.filename,
                    'additions': f.additions,
                    'deletions': f.deletions,
                    'changes': f.patch
                } for f in commit.files]
                
                commits_data.append({
                    'commit_hash': commit.sha,
                    'commit_message': commit.commit.message,
                    'commit_date': commit.commit.author.date.isoformat(),
                    'repository': repo.name,
                    'files_changed': file_changes
                })
        
        return commits_data
        
    def process_and_store_commit(self, commit_data):
        """Store a single learning log entry"""
        try:
            # check for existing commit
            if LearningLog.find_by_commit_hash(commit_data['commit_hash']):
                return False

            # create new learning log
            LearningLog.create({
                'commit_hash': commit_data['commit_hash'],
                'commit_message': commit_data['commit_message'],
                'commit_date': datetime.fromisoformat(commit_data['commit_date'].replace('Z', '+00:00')),
                'repository': commit_data['repository'],
                'lines_added': sum(f['additions'] for f in commit_data['files_changed']),
                'lines_deleted': sum(f['deletions'] for f in commit_data['files_changed']),
                'files_changed': commit_data['files_changed']
            })
            return True
        except Exception as e:
            print(f"Error storing log: {e}")
            return False
    
    def sync_logs(self):
        """Backfill all previous commits"""
        results = {'processed': 0, 'skipped': 0}
        
        # fetch and process commits
        commits = self.fetch_github_commits()
        for commit in commits:
            if self.process_and_store_commit(commit):
                results['processed'] += 1
            else:
                results['skipped'] += 1
        
        return jsonify(results)
    
    def test_extractor(self, username=None):
        """Test the extractor: fetch commits from github, excluding specific repos"""
        # Repos to exclude
        EXCLUDED_REPOS = [
            'fa23-lab-Martinlacsamana',
            'fa23-proj1-a-khani',
            'fa23-proj2-Martinlacsamana',
            'fa23-proj3-a-khani',
            'fa23-proj4-Martinlacsamana',
            'prog-02-programming-practice-starter',
            'programming-assignment-1-modal-medley-Martinlacsamana',
            'programming-assignment-2-programming-practice-Martinlacsamana',
            'programming-assignment-3-speedy-smarts-Martinlacsamana',
            'programming-assignment-3-speedy-smarts-starter',
            'sp24-proj2-martin',
            'fa24-proj0-Martinlacsamana',
            'fa24-proj1-Martinlacsamana',
            'fa24-proj2-Martinlacsamana',
            'fa24-proj3-Martinlacsamana',
            'fa24-proj4-Martinlacsamana',
            'fa24-proj5-Martinlacsamana',
            'fa24-proj6-Martinlacsamana'
        ]
        
        user = self.github.get_user(username) if username else self.github.get_user()
        
        commits_data = []
        while len(commits_data) < 10:
            for repo in user.get_repos():
                # Skip if repo is in excluded list
                if repo.name in EXCLUDED_REPOS:
                    continue
                
                for commit in repo.get_commits(author=user.login):
                    file_changes = [{
                        'filename': f.filename,
                        'additions': f.additions,
                        'deletions': f.deletions,
                    } for f in commit.files]
                
                    commits_data.append({
                        'commit_hash': commit.sha,
                        'commit_message': commit.commit.message,
                        'commit_date': commit.commit.author.date.isoformat(),
                        'repository': repo.name,
                        'files_changed': file_changes
                    })
                    print('Commit message: ', commit.commit.message)
                    
                    if len(commits_data) >= 30:
                        break
                if len(commits_data) >= 30:
                    break

        return commits_data
    
    def test_db(self):
        """Test the database by creating and retrieving a sample learning log"""
        try:
            logger.debug("Starting database test...")
            
            sample_data = {
                'commit_hash': 'test123',
                'commit_message': 'Test commit for database verification',
                'commit_date': datetime.utcnow(),
                'commit_type': 'TEST',
                'repository': 'test-repo',
                'lines_added': 10,
                'lines_deleted': 5,
                'files_changed': 1
            }

            logger.debug("Attempting to create learning log...")
            result = LearningLog.create(sample_data)
            logger.debug(f"Insert result: {result}")
            
            logger.debug("Attempting to retrieve learning log...")
            retrieved = LearningLog.find_by_commit_hash('test123')
            logger.debug(f"Retrieved data: {retrieved}")
            
            if retrieved:
                return jsonify({
                    'status': 'success',
                    'message': 'Database test successful',
                    'data': {
                        'commit_hash': retrieved['commit_hash'],
                        'commit_message': retrieved['commit_message'],
                        'repository': retrieved['repository']
                    }
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Could not retrieve test entry'
                })
            
        except Exception as e:
            logger.error(f"Database test failed: {str(e)}", exc_info=True)
            return jsonify({
                'status': 'error',
                'message': f'Database test failed: {str(e)}'
            })
