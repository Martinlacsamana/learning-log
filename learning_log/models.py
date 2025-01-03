from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class LearningLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commit_hash = db.Column(db.String(40), unique=True)
    commit_message = db.Column(db.Text)
    commit_date = db.Column(db.DateTime)
    commit_type = db.Column(db.String(20))
    repository = db.Column(db.String(255))
    lines_added = db.Column(db.Integer)
    lines_deleted = db.Column(db.Integer)
    files_changed = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 