from models import Subscription, db
from datetime import datetime, timedelta
import pytz

def create_subscription(user, plan):
    poland_timezone = pytz.timezone('Europe/Warsaw')
    now_poland = datetime.now(poland_timezone)
    
    subscription = Subscription(
        username=user.username,
        email=user.email,
        plan=plan,
        status="PENDING",
        payment_id=None,
        payment_intent=None,
        start_date=now_poland,
        end_date=now_poland + timedelta(days=30)
    )
    db.session.add(subscription)
    db.session.commit()
    return subscription

def get_active_subscription(user_id):
    return Subscription.query.filter_by(user_id=user_id, status="ACTIVE").first()