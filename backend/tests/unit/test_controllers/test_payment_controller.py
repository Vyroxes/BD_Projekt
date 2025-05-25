from unittest.mock import patch, MagicMock
from datetime import datetime
import pytz
from controllers.payment_controller import create_subscription, get_active_subscription

def test_create_subscription(app_context, mock_user):
    with patch('models.db.session.add') as mock_add, \
         patch('models.db.session.commit') as mock_commit:
        subscription = create_subscription(mock_user, "PREMIUM")
        
        assert subscription is not None
        assert subscription.username == "testuser"
        assert subscription.email == "test@example.com"
        assert subscription.plan == "PREMIUM"
        assert subscription.status == "PENDING"
        assert subscription.payment_id is None
        assert subscription.payment_intent is None
        
        now = datetime.now(pytz.timezone('Europe/Warsaw'))
        assert (now - subscription.start_date).total_seconds() < 5
        days_diff = (subscription.end_date - now).days
        assert days_diff >= 29 and days_diff <= 30
        
        mock_add.assert_called_once()
        mock_commit.assert_called_once()

def test_create_subscription_premium_plus(app_context, mock_user):
    with patch('models.db.session.add') as mock_add, \
         patch('models.db.session.commit') as mock_commit:
        subscription = create_subscription(mock_user, "PREMIUM+")
        
        assert subscription is not None
        assert subscription.username == "testuser"
        assert subscription.plan == "PREMIUM+"
        assert subscription.status == "PENDING"

def test_get_active_subscription_exists(app_context):
    mock_subscription = MagicMock()
    mock_subscription.username = "testuser"
    mock_subscription.plan = "PREMIUM"
    mock_subscription.status = "ACTIVE"
    
    with patch('models.Subscription.query') as mock_query:
        mock_query.filter_by.return_value.first.return_value = mock_subscription
        result = get_active_subscription(1)
        
        assert result == mock_subscription
        mock_query.filter_by.assert_called_once_with(user_id=1, status="ACTIVE")

def test_get_active_subscription_not_exists(app_context):
    with patch('models.Subscription.query') as mock_query:
        mock_query.filter_by.return_value.first.return_value = None
        result = get_active_subscription(1)
        
        assert result is None
        mock_query.filter_by.assert_called_once_with(user_id=1, status="ACTIVE")

def test_create_subscription_timezone(app_context, mock_user):
    with patch('models.db.session.add') as mock_add, \
         patch('models.db.session.commit') as mock_commit:
        subscription = create_subscription(mock_user, "PREMIUM")
        
        assert subscription.start_date.tzinfo is not None
        assert subscription.end_date.tzinfo is not None
        assert subscription.start_date.tzinfo.zone == 'Europe/Warsaw'
        assert subscription.end_date.tzinfo.zone == 'Europe/Warsaw'