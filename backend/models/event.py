from datetime import datetime
from models.base import db


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    issue_id = db.Column(db.BigInteger, db.ForeignKey('issues.id'), nullable=False, index=True)
    type = db.Column(db.String(64), nullable=False, index=True)
    actor = db.Column(db.String(64), nullable=False, default='system')
    payload_json = db.Column(db.JSON, nullable=True)
    ts = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    def to_dict(self):
        """Convert event to dictionary"""
        return {
            'id': self.id,
            'issue_id': self.issue_id,
            'type': self.type,
            'actor': self.actor,
            'payload': self.payload_json,
            'ts': self.ts.isoformat() if self.ts else None
        }
