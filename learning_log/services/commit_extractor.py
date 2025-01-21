''' STAGE 1: COMMIT EXTRACTION AND STORAGE '''

from github import Github, Auth
from datetime import datetime
from ..models import LearningLog
import os
from flask import jsonify
import logging
import github

logger = logging.getLogger(__name__)

class CommitExtractor:
    def __init__(self, github_token):
        # store token in instance to avoid reading env multiple times
        self.github_token = github_token
        self.github = Github(auth=Auth.Token(github_token))
    
    def fetch_filtered_commits(self, username=None):
        """Fetch all commits from non-excluded GitHub repos
        
        Args:
            username (str, optional): GitHub username to fetch commits from
        """
        # Repos to exclude (school/assignment repos)
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
        
        logger.info("Starting commit fetch from GitHub...")
        user = self.github.get_user(username) if username else self.github.get_user()
        
        commits_data = []
        for repo in user.get_repos():
            # Skip if repo is in excluded list
            if repo.name in EXCLUDED_REPOS:
                logger.info(f"Skipping excluded repo: {repo.name}")
                continue
            
            logger.info(f"Fetching commits from repo: {repo.name}")
            try:
                # Try to get commits for this repo
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
                    logger.info(f'Found commit: {commit.commit.message[:50]}...')
                    
                    if len(commits_data) % 100 == 0:
                        logger.info(f"Processed {len(commits_data)} commits so far...")
                    
            except github.GithubException as e:
                if e.status == 409:  # Empty repository
                    logger.info(f"Skipping empty repository: {repo.name}")
                    continue
                else:
                    logger.error(f"Error fetching commits from {repo.name}: {str(e)}")
                    raise

        logger.info(f"Finished fetching commits. Total found: {len(commits_data)}")
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
                'lines_added': commit_data.get('lines_added', 0),  # use pre-calculated values
                'lines_deleted': commit_data.get('lines_deleted', 0),  # use pre-calculated values
                'files_changed': commit_data.get('files_changed', 0)  # use pre-calculated value
            })
            return True
        except Exception as e:
            logger.error(f"Error storing log: {e}")
            return False
    
    def sync_logs(self):
        """Backfill all previous commits"""
        logger.info("Starting full commit sync...")
        results = {'processed': 0, 'skipped': 0}
        
        user = self.github.get_user()
        
        # Repos to exclude (school/assignment repos)
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
            'fa24-proj6-Martinlacsamana',
            'enigma-transit'
        ]
        
        for repo in user.get_repos():
            # Skip if repo is in excluded list
            if repo.name in EXCLUDED_REPOS:
                logger.info(f"Skipping excluded repo: {repo.name}")
                continue
            
            logger.info(f"Fetching commits from repo: {repo.name}")
            try:
                # Process commits one at a time
                for commit in repo.get_commits(author=user.login):
                    file_changes = [{
                        'filename': f.filename,
                        'additions': f.additions,
                        'deletions': f.deletions,
                    } for f in commit.files]
                    
                    commit_data = {
                        'commit_hash': commit.sha,
                        'commit_message': commit.commit.message,
                        'commit_date': commit.commit.author.date.isoformat(),
                        'repository': repo.name,
                        'files_changed': len(file_changes),  # store count directly
                        'lines_added': sum(f['additions'] for f in file_changes),
                        'lines_deleted': sum(f['deletions'] for f in file_changes)
                    }
                    
                    # Store immediately
                    if self.process_and_store_commit(commit_data):
                        results['processed'] += 1
                        logger.info(f'Stored commit: {commit.commit.message[:50]}...')
                    else:
                        results['skipped'] += 1
                        logger.info(f'Skipped existing commit: {commit.commit.message[:50]}...')
                    
                    # Log progress periodically
                    if (results['processed'] + results['skipped']) % 50 == 0:
                        logger.info(f"Progress: {results['processed']} stored, {results['skipped']} skipped")
                    
            except github.GithubException as e:
                if e.status == 409:  # Empty repository
                    logger.info(f"Skipping empty repository: {repo.name}")
                    continue
                else:
                    logger.error(f"Error fetching commits from {repo.name}: {str(e)}")
                    raise
        
        logger.info(f"Sync completed. Processed {results['processed']} commits, skipped {results['skipped']} commits.")
        return jsonify(results)
    
    def test_extractor(self, username=None, limit=5):
        """Test the extractor: fetch commits from github, excluding specific repos
        
        Args:
            username (str, optional): GitHub username to fetch commits
            limit (int, optional): Maximum number of commits to fetch (default 5)
        """
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
                logger.info(f'Found commit: {commit.commit.message}')
                
                # Return early once we have enough commits
                if len(commits_data) >= limit:
                    return commits_data

            
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

    def test_extractor_and_store(self, username=None, limit=3):
        """Test both extraction and storage of commits
        
        Args:
            username (str, optional): GitHub username to fetch commits from
            limit (int, optional): Number of commits to store (default 3)
        """
        try:
            logger.debug(f"Starting extractor and storage test for {limit} commits...")
            
            # Get test commits
            commits = self.test_extractor(username)[:limit]
            
            results = {
                'status': 'success',
                'total_fetched': len(commits),
                'stored_commits': [],
                'errors': []
            }
            
            # Try to store each commit
            for commit in commits:
                try:
                    # add required fields for storage
                    storage_data = {
                        **commit,
                        'files_changed': len(commit['files_changed']),  # convert list to count
                        'lines_added': sum(f['additions'] for f in commit['files_changed']),
                        'lines_deleted': sum(f['deletions'] for f in commit['files_changed'])
                    }
                    
                    if self.process_and_store_commit(storage_data):
                        results['stored_commits'].append({
                            'commit_hash': commit['commit_hash'],
                            'commit_message': commit['commit_message'],
                            'repository': commit['repository']
                        })
                    else:
                        results['errors'].append(f"Failed to store commit {commit['commit_hash']}")
                
                except Exception as e:
                    results['errors'].append(f"Error processing commit {commit['commit_hash']}: {str(e)}")
            
            results['stored_count'] = len(results['stored_commits'])
            results['error_count'] = len(results['errors'])
            
            return jsonify(results)
            
        except Exception as e:
            logger.error(f"Test failed: {str(e)}", exc_info=True)
            return jsonify({
                'status': 'error',
                'message': f'Extractor and storage test failed: {str(e)}'
            })
