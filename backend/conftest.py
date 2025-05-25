from datetime import timedelta
import json
from unittest.mock import MagicMock
import pytest
from main import app
from models import db
from models.user import User
from models.book_collection import BookCollection
from models.wishlist import WishList
from flask_bcrypt import generate_password_hash
from flask_jwt_extended import create_access_token

@pytest.fixture
def app_instance():
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app_instance):
    return app_instance.test_client()

@pytest.fixture
def user(app_instance):
    hashed_password = generate_password_hash("Testuser1.").decode('utf-8')   
    with app_instance.app_context():    
        existing_user = User.query.filter_by(username="testuser").first()
        if existing_user:
            return existing_user
            
        test_user = User(
            username="testuser",
            email="testuser@example.com",
            password=hashed_password
        )
        db.session.add(test_user)
        db.session.commit()
        return test_user

@pytest.fixture
def auth_token(app_instance):
    with app_instance.app_context():
        test_user = User.query.filter_by(username="testuser").first()
        if not test_user:
            hashed_password = generate_password_hash("Testuser1.").decode('utf-8')
            test_user = User(
                username="testuser", 
                email="testuser@example.com",
                password=hashed_password
            )
            db.session.add(test_user)
            db.session.commit()
        
        access_token = create_access_token(
            identity=str(test_user.id),
            expires_delta=timedelta(minutes=10)
        )
        return access_token
    
@pytest.fixture
def book_in_collection(client, auth_token, user):
    with client.application.app_context():
        book = BookCollection.query.filter_by(user_id=user.id).first()
        
        if not book:
            response = client.post(
                '/api/add-book/bc',
                data=json.dumps({
                    "title": "Test Book",
                    "author": "Test Author",
                    "cover": "test.jpg",
                    "genres": "fantasy",
                    "publisher": "Test Publisher",
                    "date": "2023-01-01",
                    "pages": 123,
                    "isbn": "9781234567897",
                    "desc": "Test description."
                }),
                headers={'Authorization': f'Bearer {auth_token}'},
                content_type='application/json'
            )
            assert response.status_code == 201
            book = BookCollection.query.filter_by(user_id=user.id).first()
        
        return book.id

@pytest.fixture
def book_in_wishlist(client, auth_token, user):
    with client.application.app_context():
        book = WishList.query.filter_by(user_id=user.id).first()
        
        if not book:
            response = client.post(
                '/api/add-book/wl',
                data=json.dumps({
                    "title": "Wishlist Book",
                    "author": "Wishlist Author",
                    "cover": "wishlist.jpg",
                    "genres": "SciFi",
                    "publisher": "Wishlist Publisher",
                    "date": "2023-02-02",
                    "pages": 234,
                    "isbn": "9781234567898",
                    "desc": "Wishlist description"
                }),
                headers={'Authorization': f'Bearer {auth_token}'},
                content_type='application/json'
            )
            assert response.status_code == 201
            book = WishList.query.filter_by(user_id=user.id).first()
        
        return book.id
    
@pytest.fixture
def mock_discord_user():
    mock_user = MagicMock()
    mock_user.id = "123456789"
    mock_user.name = "discord_user"
    mock_user.email = "discord_user@example.com"
    mock_user.avatar_url = "https://cdn.discordapp.com/avatars/123456789/abcdef.png"
    return mock_user

@pytest.fixture
def mock_github_response():
    return {
        "id": 987654321,
        "login": "github_user",
        "email": "github_user@example.com",
        "avatar_url": "https://avatars.githubusercontent.com/u/987654321"
    }

@pytest.fixture
def mock_stripe_session():
    mock = MagicMock()
    mock.id = "cs_test_123456789"
    mock.url = "https://checkout.stripe.com/test"
    return mock

@pytest.fixture
def app_context():
    with app.app_context():
        yield

@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    return user

@pytest.fixture
def app_context():
    with app.app_context():
        yield