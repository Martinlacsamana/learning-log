import os

class Config:
    MONGO_URI = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/learning_log') 