from unittest.mock import patch, MagicMock
from models.user import User
from models.subscription import Subscription
from datetime import datetime, timedelta
import pytz

def test_payments_create(client, auth_token, user, app_instance):
    with patch('routes.payment_routes.stripe.checkout.Session.create') as mock_create, \
         patch('routes.payment_routes.db.session.add'), \
         patch('routes.payment_routes.db.session.commit'):
        
        mock_session = MagicMock()
        mock_session.id = "cs_test_123456789"
        mock_session.url = "https://checkout.stripe.com/test"
        mock_create.return_value = mock_session
        
        response = client.post(
            '/api/payments/create',
            json={"plan": "PREMIUM"},
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 200
        assert "payment_url" in response.json
        assert response.json["payment_url"] == "https://checkout.stripe.com/test"
        assert "subscription_id" in response.json

def test_payments_create_invalid_plan(client, auth_token):
    response = client.post(
        '/api/payments/create',
        json={"plan": "INVALID_PLAN"},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 400
    assert "Nieprawidłowy plan" in response.json["error"]

def test_payments_set_unauthorized(client, auth_token, user):
    response = client.post(
        '/api/payments/set/other_user',
        json={"plan": "PREMIUM", "status": "ACTIVE"},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 403
    assert "Brak uprawnień" in response.json["error"]

def test_payments_status(client, auth_token, user, app_instance):
    with patch('routes.payment_routes.db.session.get') as mock_session_get, \
         patch('routes.payment_routes.User.query.filter_by') as mock_user_filter, \
         patch('routes.payment_routes.Subscription.query.filter_by') as mock_sub_filter:
        
        mock_session_get.return_value = user
        
        mock_target_user = MagicMock()
        mock_target_user.username = user.username
        mock_user_filter.return_value.first.return_value = mock_target_user
        
        mock_sub = MagicMock()
        mock_sub.status = "ACTIVE"
        mock_sub.plan = "PREMIUM"
        mock_sub.end_date = datetime.now(pytz.timezone('Europe/Warsaw')) + timedelta(days=10)
        
        mock_sub_filter.return_value.order_by.return_value.first.side_effect = [None, mock_sub]
        
        response = client.get(
            f'/api/payments/status/{user.username}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 200
        assert "has_premium" in response.json

def test_payments_status_expired(client, auth_token, user, app_instance):
    with patch('routes.payment_routes.db.session.get') as mock_session_get, \
         patch('routes.payment_routes.User.query.filter_by') as mock_user_filter, \
         patch('routes.payment_routes.Subscription.query.filter_by') as mock_sub_filter, \
         patch('routes.payment_routes.db.session.commit'):
        
        mock_session_get.return_value = user
        
        mock_target_user = MagicMock()
        mock_target_user.username = user.username
        mock_user_filter.return_value.first.return_value = mock_target_user
        
        mock_sub = MagicMock()
        mock_sub.status = "ACTIVE"
        mock_sub.plan = "PREMIUM"
        mock_sub.end_date = datetime.now(pytz.timezone('Europe/Warsaw')) - timedelta(days=1)
        
        def side_effect(*args, **kwargs):
            if kwargs.get("status") == "PENDING":
                return MagicMock(order_by=lambda *a: MagicMock(first=lambda: None))
            else:
                return MagicMock(order_by=lambda *a: MagicMock(first=lambda: mock_sub))
        
        mock_sub_filter.side_effect = side_effect
        
        response = client.get(
            f'/api/payments/status/{user.username}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 200
        assert response.json["has_premium"] == False

def test_payments_status_no_subscription(client, auth_token, user):
    with patch('routes.payment_routes.Subscription.query.filter_by') as mock_filter:
        mock_filter.return_value.order_by.return_value.first.return_value = None
        
        response = client.get(
            f'/api/payments/status/{user.username}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 200
        assert response.json["has_premium"] == False
        assert "Użytkownik nie ma subskrypcji" in response.json["message"]

def test_payments_webhook_checkout_completed(client, app_instance):
    with patch('routes.payment_routes.stripe.Webhook.construct_event') as mock_construct, \
         patch('routes.payment_routes.db.session.get') as mock_get, \
         patch('routes.payment_routes.db.session.commit'):
        
        event = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_test_123456789',
                    'payment_intent': 'pi_test_123456789',
                    'metadata': {
                        'userId': '1',
                        'subscriptionId': '1'
                    }
                }
            }
        }
        
        mock_construct.return_value = event
        
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        
        mock_subscription = MagicMock()
        mock_subscription.status = "PENDING"
        mock_subscription.plan = "PREMIUM"
        mock_subscription.username = "testuser"
        
        def side_effect(model, id):
            if model == User and id == '1':
                return mock_user
            if model == Subscription and id == '1':
                return mock_subscription
        
        mock_get.side_effect = side_effect
        
        response = client.post(
            '/api/payments/webhook',
            headers={'stripe-signature': 'test_signature'}
        )
        
        assert response.status_code == 200
        assert mock_subscription.status == "ACTIVE"

def test_payments_webhook_invalid_signature(client):
    with patch('routes.payment_routes.stripe.Webhook.construct_event') as mock_construct:
        mock_construct.side_effect = Exception("Invalid signature")
        
        response = client.post(
            '/api/payments/webhook',
            headers={'stripe-signature': 'invalid_signature'}
        )
        
        assert response.status_code == 400
        assert b"Nieprawid" in response.data