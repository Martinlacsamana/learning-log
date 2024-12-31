from app.database import db
from app.models.learning_log import LearningLog
from app.services.github_service import fetch_github_commits
from app.services.openai_service import generate_commit_summary

class LearningLogService:
    @staticmethod
    def store_log(commit_data, summary):
        """Store a single learning log entry"""
        try:
            existing_log = LearningLog.query.filter_by(commit_hash=commit_data['commit_hash']).first()
            if existing_log:
                print(f"Commit {commit_data['commit_hash']} already exists in database")
                return False

            log_entry = LearningLog(
                commit_hash=commit_data['commit_hash'],
                commit_message=commit_data['commit_message'],
                commit_date=commit_data['commit_date'],
                summary=summary,
                repository=commit_data['repository']
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
        """Sync all commits and generate learning logs"""
        results = {'processed': 0, 'failed': 0, 'skipped': 0}
        
        commits = fetch_github_commits(username, since)
        for commit in commits:
            summary = generate_commit_summary(commit['commit_message'], commit['repository'])
            if LearningLogService.store_log(commit, summary):
                results['processed'] += 1
            else:
                results['skipped'] += 1
        
        return results

    @staticmethod
    def get_all_logs():
        """Retrieve all learning logs"""
        return LearningLog.query.order_by(LearningLog.commit_date.desc()).all() 