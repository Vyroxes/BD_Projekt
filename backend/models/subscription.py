from sqlalchemy import CheckConstraint, func
from . import db
from datetime import datetime
import pytz

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(320), nullable=False)
    plan = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='PENDING', server_default='PENDING')
    payment_id = db.Column(db.String(100), nullable=True)
    payment_intent = db.Column(db.String(100), nullable=True)
    start_date = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(pytz.timezone('Europe/Warsaw')),
        server_default=func.now()
    )
    end_date = db.Column(db.DateTime, nullable=False)

    __table_args__ = (
        CheckConstraint("plan IN ('PREMIUM', 'PREMIUM+')", name='check_plan_valid'),
        CheckConstraint("status IN ('PENDING', 'ACTIVE', 'EXPIRED', 'CANCELLED')", name='check_status_valid'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "plan": self.plan,
            "status": self.status,
            "payment_id": self.payment_id,
            "payment_intent": self.payment_intent,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
        }