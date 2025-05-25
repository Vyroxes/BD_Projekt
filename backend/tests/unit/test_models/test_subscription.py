import pytest
from datetime import datetime, timedelta
import pytz
from models.subscription import Subscription
from main import app

@pytest.fixture
def app_context():
    with app.app_context():
        yield

def test_create_subscription():
    now = datetime.now(pytz.timezone('Europe/Warsaw'))
    end_date = now + timedelta(days=30)
    
    subscription = Subscription(
        username="testuser",
        email="test@example.com",
        plan="PREMIUM",
        status="PENDING",
        start_date=now,
        end_date=end_date
    )
    
    assert subscription.username == "testuser"
    assert subscription.email == "test@example.com"
    assert subscription.plan == "PREMIUM"
    assert subscription.status == "PENDING"
    assert subscription.payment_id is None
    assert subscription.payment_intent is None
    assert subscription.start_date == now
    assert subscription.end_date == end_date

def test_to_dict_method():
    now = datetime.now(pytz.timezone('Europe/Warsaw'))
    end_date = now + timedelta(days=30)
    
    subscription = Subscription(
        id=1,
        username="testuser",
        email="test@example.com",
        plan="PREMIUM",
        status="ACTIVE",
        payment_id="payment_123",
        payment_intent="intent_123",
        start_date=now,
        end_date=end_date
    )
    
    subscription_dict = subscription.to_dict()
    
    assert subscription_dict["id"] == 1
    assert subscription_dict["username"] == "testuser"
    assert subscription_dict["email"] == "test@example.com"
    assert subscription_dict["plan"] == "PREMIUM"
    assert subscription_dict["status"] == "ACTIVE"
    assert subscription_dict["payment_id"] == "payment_123"
    assert subscription_dict["payment_intent"] == "intent_123"
    assert subscription_dict["start_date"] == now.isoformat()
    assert subscription_dict["end_date"] == end_date.isoformat()

def test_valid_plan_values():
    valid_plans = ["PREMIUM", "PREMIUM+"]
    
    for plan in valid_plans:
        subscription = Subscription(
            username="testuser",
            email="test@example.com",
            plan=plan,
            status="PENDING",
            start_date=datetime.now(pytz.timezone('Europe/Warsaw')),
            end_date=datetime.now(pytz.timezone('Europe/Warsaw')) + timedelta(days=30)
        )
        assert subscription.plan == plan

def test_valid_status_values():
    valid_statuses = ["PENDING", "ACTIVE", "EXPIRED", "CANCELLED"]
    
    for status in valid_statuses:
        subscription = Subscription(
            username="testuser",
            email="test@example.com",
            plan="PREMIUM",
            status=status,
            start_date=datetime.now(pytz.timezone('Europe/Warsaw')),
            end_date=datetime.now(pytz.timezone('Europe/Warsaw')) + timedelta(days=30)
        )
        assert subscription.status == status

def test_subscription_defaults():
    end_date = datetime.now(pytz.timezone('Europe/Warsaw')) + timedelta(days=30)
    
    subscription = Subscription(
        username="testuser",
        email="test@example.com",
        plan="PREMIUM",
        status="PENDING",
        end_date=end_date
    )
    
    assert subscription.status == "PENDING"

def test_nullable_fields():
    now = datetime.now(pytz.timezone('Europe/Warsaw'))
    end_date = now + timedelta(days=30)
    
    subscription = Subscription(
        username="testuser",
        email="test@example.com",
        plan="PREMIUM",
        status="PENDING",
        start_date=now,
        end_date=end_date
    )
    
    assert subscription.payment_id is None
    assert subscription.payment_intent is None

def test_premium_plus_plan():
    now = datetime.now(pytz.timezone('Europe/Warsaw'))
    end_date = now + timedelta(days=30)
    
    subscription = Subscription(
        username="testuser",
        email="test@example.com",
        plan="PREMIUM+",
        status="PENDING",
        start_date=now,
        end_date=end_date
    )
    
    assert subscription.plan == "PREMIUM+"

def test_to_dict_with_none_dates():
    subscription = Subscription(
        id=1,
        username="testuser",
        email="test@example.com",
        plan="PREMIUM",
        status="PENDING",
        start_date=None,
        end_date=None
    )
    
    subscription_dict = subscription.to_dict()
    
    assert subscription_dict["start_date"] is None
    assert subscription_dict["end_date"] is None