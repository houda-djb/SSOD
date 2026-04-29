from app.models import db
from datetime import datetime, timezone

class Alert(db.Model):
    __tablename__ = "alerts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    severity = db.Column(db.String(20), nullable=False, default="low")
    category = db.Column(db.String(50), nullable=False, default="system")
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    source = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="open")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    resolved_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "severity": self.severity,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "source": self.source,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }