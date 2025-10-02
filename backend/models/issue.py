from datetime import datetime
from models.base import db


class Issue(db.Model):
    __tablename__ = 'issues'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    title = db.Column(db.String(500), nullable=False)
    type = db.Column(db.Enum('BUG', 'STORY', 'TASK', name='issue_type'), nullable=False, default='BUG')
    state = db.Column(db.Enum('New', 'Active', 'Resolved', 'Closed', 'Removed', name='issue_state'),
                     nullable=False, default='New', index=True)
    created_by = db.Column(db.String(64), nullable=False, default='system')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow,
                          onupdate=datetime.utcnow)

    events = db.relationship('Event', backref='issue', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        """Convert issue to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'type': self.type,
            'state': self.state,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
