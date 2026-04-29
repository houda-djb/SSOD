from app.models import db
from datetime import datetime, timezone

class Metric(db.Model):
    __tablename__ = "metrics"
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100), nullable=False, default="main_server")
    metric_type = db.Column(db.String(50), nullable=False, index=True)
    metric_name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=True)
    threshold_breached = db.Column(db.Boolean, default=False)
    threshold_value = db.Column(db.Float, nullable=True)
    recorded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "source": self.source,
            "metric_type": self.metric_type,
            "metric_name": self.metric_name,
            "value": self.value,
            "unit": self.unit,
            "threshold_breached": self.threshold_breached,
            "threshold_value": self.threshold_value,
            "recorded_at": self.recorded_at.isoformat(),
        }