from flask import Blueprint, jsonify
from .views import fetch_github_commits, store_learning_log, classify_commit
from .models import LearningLog

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return 'Learning Log'

@bp.route('/sync')
def sync_logs():
    results = {'processed': 0, 'skipped': 0}
    
    commits = fetch_github_commits()
    for commit in commits:
        if store_learning_log(commit):
            results['processed'] += 1
        else:
            results['skipped'] += 1
    
    return jsonify(results)

@bp.route('/logs')
def get_logs():
    logs = LearningLog.query.order_by(LearningLog.commit_date.desc()).all()
    return jsonify([{
        'id': log.id,
        'commit_hash': log.commit_hash,
        'commit_message': log.commit_message,
        'commit_date': log.commit_date.isoformat(),
        'repository': log.repository,
        'created_at': log.created_at.isoformat()
    } for log in logs]) 