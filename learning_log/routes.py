from flask import Blueprint, jsonify
from .services.commit_extractor import CommitExtractor
from .models import LearningLog
import os

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return 'Learning Log'

''' STAGE 1: COMMIT EXTRACTION AND STORAGE '''

@bp.route('/testExtractor')
def testCommitExtractor():
    extractor = CommitExtractor(os.getenv('GITHUB_TOKEN'))
    return jsonify(extractor.test_extractor())

@bp.route('/sync')
def sync_logs():
    # create extractor instance with github token
    extractor = CommitExtractor(os.getenv('GITHUB_TOKEN'))
    # call the sync_logs method
    return extractor.sync_logs()

''' END STAGE 1 '''

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