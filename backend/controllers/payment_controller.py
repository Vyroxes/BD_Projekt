from models import Subscription, db
from datetime import datetime, timedelta
import pytz

def create_subscription(user, plan):
    poland_timezone = pytz.timezone('Europe/Warsaw')
    now_poland = datetime.now(poland_timezone)
    subscription = Subscription(
        user_id=user.id,
        stripe_subscription_id="",
        status="PENDING",
        current_period_end=now_poland + timedelta(days=30),
        created_at=now_poland
    )
    db.session.add(subscription)
    db.session.commit()
    return subscription

def get_active_subscription(user_id):
    return Subscription.query.filter_by(user_id=user_id, status="ACTIVE").first()