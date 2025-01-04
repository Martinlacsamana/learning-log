from flask_pymongo import PyMongo
from datetime import datetime
from typing import List, Dict, Any  # type hints for clarity

mongo = PyMongo()

class LearningLog:
    # Define document structure with type hints
    SCHEMA = {
        'commit_hash': str,
        'commit_message': str,
        'commit_date': datetime,
        'commit_type': str,
        'repository': str,
        'lines_added': int,
        'lines_deleted': int,
        'files_changed': List[Dict[str, Any]],  # array of file change objects
        'created_at': datetime
    }
    
    def __init__(self, **kwargs):
        # you can add validation here if needed
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def create(cls, data: dict):
        # validate files_changed format
        if not isinstance(data.get('files_changed'), list):
            raise ValueError("files_changed must be a list of file changes")
            
        # ensure each file change has required fields
        for file_change in data['files_changed']:
            if not all(k in file_change for k in ('filename', 'additions', 'deletions')):
                raise ValueError("Each file change must have filename, additions, and deletions")
        
        data['created_at'] = datetime.utcnow()
        return mongo.db.learning_logs.insert_one(data)
    
    @classmethod
    def find_by_commit_hash(cls, commit_hash):
        return mongo.db.learning_logs.find_one({'commit_hash': commit_hash})
    
    @classmethod
    def get_all(cls):
        # returns cursor that can be iterated
        return mongo.db.learning_logs.find().sort('commit_date', -1)
    
    @classmethod
    def find_by_type(cls, commit_type):
        return mongo.db.learning_logs.find({'commit_type': commit_type}) 