from datetime import datetime
from learning_log import mongo
import logging

logger = logging.getLogger(__name__)

class LearningLog:
    # Define document structure with type hints
    SCHEMA = {
        # Required fields
        'commit_hash': str,
        'commit_message': str,
        'commit_date': datetime,
        'repository': str,
        'lines_added': int,
        'lines_deleted': int,
        'files_changed': int,  # number of files changed
        'created_at': datetime,
        
        # Optional field - will be populated by classification endpoint later
        'commit_type': str | None  # make it optional by allowing None
    }
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def create(cls, data: dict):
        logger.debug("Attempting to create learning log...")
        logger.debug(f"Current app db exists: {hasattr(mongo, 'db')}")
        
        if hasattr(mongo, 'db'):
            logger.debug(f"DB collections: {mongo.db.list_collection_names()}")
        else:
            logger.error("No db attribute found on db")
            
        # Only validate required fields
        if not isinstance(data.get('files_changed'), int):
            logger.error("files_changed must be an integer")
            raise ValueError("files_changed must be an integer")
        
        # Set created_at timestamp
        data['created_at'] = datetime.utcnow()
        
        # commit_type can be None or omitted entirely
        data.setdefault('commit_type', None)
        
        # Create collection if it doesn't exist
        if 'learning_logs' not in mongo.db.list_collection_names():
            logger.debug("Creating learning_logs collection...")
            mongo.db.create_collection('learning_logs')
            
        return mongo.db.learning_logs.insert_one(data)
    
    @classmethod
    def find_by_commit_hash(cls, commit_hash):
        return mongo.db.learning_logs.find_one({'commit_hash': commit_hash})
    
    @classmethod
    def get_all(cls):
        return mongo.db.learning_logs.find().sort('commit_date', -1)
    
    @classmethod
    def find_by_type(cls, commit_type):
        return mongo.db.learning_logs.find({'commit_type': commit_type})
    
    @classmethod
    def find_unclassified(cls, limit=5):  # default to 15 for safety
        """Find a batch of unclassified commits
        
        Args:
            limit (int, optional): Maximum number of commits to return (default: 15)
        """
        # Apply limit in the query itself for better performance
        pipeline = [
            {'$match': {'commit_type': None}},  # find unclassified
            {'$sort': {'commit_date': -1}},     # newest first
            {'$limit': limit}                   # limit at database level
        ]
        
        return mongo.db.learning_logs.aggregate(pipeline) 