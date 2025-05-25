from unittest.mock import patch
from models.user import User
from models import db
from models.subscription import Subscription
from datetime import datetime, timedelta

def test_get_user(client, auth_token, user):
    response = client.get(
        f'/api/user/{user.username}',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200
    data = response.json
    assert data['username'] == user.username
    assert data['email'] == user.email
    assert 'avatar_url' in data
    assert 'book_collection' in data
    assert 'wish_list' in data
    assert 'account_created' in data

def test_get_nonexistent_user(client, auth_token):
    response = client.get(
        '/api/user/nonexistentuser',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 404
    assert response.json['message'] == 'Użytkownik nie istnieje.'

def test_get_all_users(client, auth_token, user):
    response = client.get(
        '/api/users',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    assert len(data) >= 1
    
    usernames = [u['username'] for u in data]
    assert user.username in usernames

def test_delete_own_account(client, auth_token, user):
    response = client.delete(
        f'/api/delete-account/{user.username}',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200
    assert 'zostało pomyślnie usunięte' in response.json['message']
    
    with client.application.app_context():
        assert db.session.get(User, user.id) is None

@patch('os.getenv')
def test_delete_account_as_admin(mock_getenv, client, app_instance):
    mock_getenv.return_value = "admin"
    
    with app_instance.app_context():
        admin = User(
            username="admin",
            email="admin@example.com",
            password="AdminPassword123!"
        )
        db.session.add(admin)
        
        regular_user = User(
            username="user_to_delete",
            email="delete@example.com",
            password="Password123!"
        )
        db.session.add(regular_user)
        db.session.commit()
        
        from flask_jwt_extended import create_access_token
        admin_token = create_access_token(identity=str(admin.id))
    
    response = client.delete(
        '/api/delete-account/user_to_delete',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    
    assert response.status_code == 200
    assert 'zostało pomyślnie usunięte' in response.json['message']

def test_delete_other_account_unauthorized(client, auth_token, app_instance):
    with app_instance.app_context():
        other_user = User(
            username="other_user",
            email="other@example.com",
            password="Password123!"
        )
        db.session.add(other_user)
        db.session.commit()
    
    response = client.delete(
        '/api/delete-account/other_user',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 403
    assert 'Brak uprawnień' in response.json['message']
    
    with client.application.app_context():
        assert User.query.filter_by(username="other_user").first() is not None

def test_delete_nonexistent_account(client, auth_token):
    response = client.delete(
        '/api/delete-account/nonexistent_user',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 404
    assert response.json['message'] == 'Użytkownik nie istnieje.'

def test_get_user_with_subscription(client, auth_token, user, app_instance):
    with app_instance.app_context():
        subscription = Subscription(
            username=user.username,
            email=user.email,
            plan="PREMIUM",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
            status="ACTIVE"
        )
        db.session.add(subscription)
        db.session.commit()
    
    response = client.get(
        f'/api/user/{user.username}',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200
    data = response.json
    assert data['premium'] == "PREMIUM"
    assert 'premium_expiration' in data