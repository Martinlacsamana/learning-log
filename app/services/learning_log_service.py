from app.database import db
from app.models.learning_log import LearningLog
from app.services.github_service import fetch_github_commits
from app.services.openai_service import batch_classify_commits
from datetime import datetime

class LearningLogService:
    @staticmethod
    def store_log(commit_data):
        """Store a single learning log entry from a commit"""
        try:
            # Check if commit already exists
            existing_log = LearningLog.query.filter_by(commit_hash=commit_data['commit_hash']).first()
            if existing_log:
                print(f"Commit {commit_data['commit_hash']} already exists in database")
                return False

            # Calculate code changes statistics
            total_additions = sum(f['additions'] for f in commit_data['files_changed'])
            total_deletions = sum(f['deletions'] for f in commit_data['files_changed'])

            # Create new log entry
            log_entry = LearningLog(
                commit_hash=commit_data['commit_hash'],
                commit_message=commit_data['commit_message'],
                commit_date=datetime.fromisoformat(commit_data['commit_date'].replace('Z', '+00:00')),
                repository=commit_data['repository'],
                lines_added=total_additions,
                lines_deleted=total_deletions,
                files_changed=commit_data['files_changed'],  # Store the full files data as JSON
                commit_type=None  # Will be classified by OpenAI later
            )
            
            db.session.add(log_entry)
            db.session.commit()
            return True

        except Exception as e:
            print(f"Error storing learning log: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def sync_logs(username=None, since=None):
        """Sync all commits and store as learning logs"""
        results = {'processed': 0, 'failed': 0, 'skipped': 0}
        
        # Fetch commits from GitHub
        commits = fetch_github_commits(username, since)
        
        # Store each commit as a learning log
        for commit in commits:
            if LearningLogService.store_log(commit):
                results['processed'] += 1
            else:
                results['skipped'] += 1

        # Classify all unclassified commits
        classification_results = batch_classify_commits()
        
        results['classified'] = classification_results['processed']
        results['classification_failed'] = classification_results['failed']
        
        return results

    @staticmethod
    def get_all_logs():
        """Retrieve all learning logs"""
        return LearningLog.query.order_by(LearningLog.commit_date.desc()).all() 