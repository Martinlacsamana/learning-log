from flask import Flask
from flask_pymongo import PyMongo
import os
import logging
from dotenv import load_dotenv
from pathlib import Path

# Force reload environment variables
base_dir = Path(__file__).parent.parent
env_path = base_dir / '.env'
load_dotenv(env_path, override=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# MongoDB Configuration
mongo_uri = os.getenv('MONGO_URI')

logger.debug(f"Mongo URI: {mongo_uri}")
app.config.update(
    MONGO_URI=mongo_uri,
    MONGO_DBNAME='learning-logs',
    MONGO_TLS=True,
    MONGO_CONNECT=True
)

try:
    # Initialize MongoDB
    mongo = PyMongo(app)
    
    # Test connection explicitly
    mongo.db.command('ping')
    logger.debug("Successfully connected to MongoDB")
    logger.debug(f"Available collections: {mongo.db.list_collection_names()}")
    
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}", exc_info=True)
    raise RuntimeError(f"MongoDB connection failed: {str(e)}")

# Import routes after app is created
from .routes import bp
app.register_blueprint(bp)