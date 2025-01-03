from app.database import db
from datetime import datetime

class LearningLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commit_hash = db.Column(db.String(40), unique=True)
    commit_date = db.Column(db.DateTime)
    commit_type = db.Column(db.String(20))  # from our predefined types
    repository = db.Column(db.String(255))
    lines_added = db.Column(db.Integer)
    lines_deleted = db.Column(db.Integer)
    files_changed = db.Column(db.JSON)  # store file changes as JSON
    technical_notes = db.Column(db.Text, nullable=True)  # optional field for specific technical details
    created_at = db.Column(db.DateTime, default=datetime.utcnow)