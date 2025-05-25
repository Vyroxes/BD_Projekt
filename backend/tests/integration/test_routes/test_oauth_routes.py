from unittest.mock import patch, MagicMock
from models import db
from models.user import User
from flask_bcrypt import Bcrypt

def test_login_discord(client):
    with patch('routes.oauth_routes.discord.create_session') as mock_create_session:
        mock_create_session.return_value = "https://discord.com/api/oauth2/authorize"
        response = client.get('/api/login/discord')
        assert mock_create_session.called
        assert mock_create_session.call_args[1]['scope'] == ["identify", "email"]
        assert response.status_code == 200 or response.status_code == 302

def test_login_github(client):
    with patch('routes.oauth_routes.oauth.github.authorize_redirect') as mock_authorize:
        mock_authorize.return_value = "https://github.com/login/oauth/authorize"
        response = client.get('/api/login/github')
        assert mock_authorize.called
        assert response.status_code == 200 or response.status_code == 302

def test_auth_discord_existing_user(client, mock_discord_user, app_instance):
    with app_instance.app_context():
        user = User(
            username="existing_discord_user",
            email="discord_user@example.com",
            password="password123"
        )
        db.session.add(user)
        db.session.commit()
    
    with patch('routes.oauth_routes.discord.callback') as mock_callback, \
         patch('routes.oauth_routes.discord.fetch_user') as mock_fetch_user, \
         patch('routes.oauth_routes.os.getenv') as mock_getenv:
        
        mock_callback.return_value = {"access_token": "fake_token"}
        mock_fetch_user.return_value = mock_discord_user
        mock_getenv.return_value = "http://localhost:3000"
        
        response = client.get('/api/auth/discord')
        
        assert response.status_code == 302
        redirect_url = response.headers['Location']
        assert redirect_url.startswith("http://localhost:3000/auth-callback")

def test_auth_github_link_account(client, mock_github_response, app_instance):
    with app_instance.app_context():
        user = User(
            username="existing_user",
            email="user@example.com",
            password="password123"
        )
        db.session.add(user)
        db.session.commit()
        
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=str(user.id))
    
    with patch('routes.oauth_routes.oauth.github.authorize_access_token') as mock_authorize, \
         patch('routes.oauth_routes.oauth.github.get') as mock_get, \
         patch('routes.oauth_routes.db.session.get') as mock_session_get:
        
        mock_authorize.return_value = {"access_token": "fake_github_token"}
        
        mock_get_instance = MagicMock()
        mock_get_instance.json.return_value = mock_github_response
        mock_get.return_value = mock_get_instance
        
        mock_session_get.return_value = user
        
        response = client.get(
            '/api/auth/github?link=true',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        assert response.status_code == 200
        assert response.json["message"] == "Konto GitHub zostało pomyślnie powiązane."

def test_auth_github_error(client):
    response = client.get('/api/auth/github?error=access_denied')
    assert response.status_code == 302
    assert response.headers['Location'] == "/login"