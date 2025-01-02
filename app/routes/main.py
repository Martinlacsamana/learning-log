from flask import Blueprint, jsonify
from datetime import datetime
from app.services.github_service import fetch_github_commits
from app.services.openai_service import generate_commit_summary
from app.services.learning_log_service import LearningLogService
import os
from pathlib import Path

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return 'Learning Log'

@main_bp.route('/fetch-commits')
def fetch_commits():
    commits = fetch_github_commits()
    return jsonify({"message": f"Found {len(commits)} commits", "commits": commits})

@main_bp.route('/test-summary')
def test_summary():
    example_commits = [
        {
            'commit_hash': '123abc',
            'commit_message': """
            feat(api): Implement Redis caching for API responses
            
            - Added Redis cache layer for frequently accessed endpoints
            - Implemented cache invalidation strategy
            - Added cache hit/miss monitoring
            - Reduced average response time by 60%
            """,
            'repository': 'backend-service',
            'commit_date': datetime.now().isoformat()
        }
    ]
    
    results = []
    for commit in example_commits:
        summary = generate_commit_summary(commit['commit_message'], commit['repository'])
        results.append({
            'original_commit': commit,
            'learning_summary': summary
        })
    
    return jsonify(results)

@main_bp.route('/sync-learning-logs')
def sync_learning_logs():
    try:
        results = LearningLogService.sync_logs()
        return jsonify({
            'status': 'success',
            'message': f"Processed {results['processed']} commits, "
                      f"skipped {results['skipped']} existing commits, "
                      f"failed {results['failed']} commits"
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@main_bp.route('/learning-logs')
def get_learning_logs():
    try:
        logs = LearningLogService.get_all_logs()
        return jsonify([{
            'id': log.id,
            'commit_hash': log.commit_hash,
            'commit_message': log.commit_message,
            'commit_date': log.commit_date.isoformat(),
            'summary': log.summary,
            'repository': log.repository,
            'created_at': log.created_at.isoformat()
        } for log in logs])
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500 

@main_bp.route('/debug-env')
def debug_env():
    return jsonify({
        'has_token': bool(os.getenv('GITHUB_TOKEN')),
        'token_length': len(os.getenv('GITHUB_TOKEN', '')),
        'env_path': str(Path(__file__).resolve().parent.parent.parent / '.env'),
        'exists': (Path(__file__).resolve().parent.parent.parent / '.env').exists()
    }) 