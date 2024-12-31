from app.database import db
from datetime import datetime

class LearningLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commit_hash = db.Column(db.String(40), unique=True)
    commit_message = db.Column(db.Text)
    commit_date = db.Column(db.DateTime)
    summary = db.Column(db.Text)
    repository = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 