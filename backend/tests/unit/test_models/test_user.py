from datetime import datetime
import pytz
from models.user import User

def test_create_user():
    now = datetime.now(pytz.timezone('Europe/Warsaw'))
    
    user = User(
        username="testuser",
        email="test@example.com",
        password="password123",
        avatar="https://example.com/avatar.jpg",
        github_id="123456789",
        discord_id="123456789012345678",
        created_at=now
    )
    
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password == "password123"
    assert user.avatar == "https://example.com/avatar.jpg"
    assert user.github_id == "123456789"
    assert user.discord_id == "123456789012345678"
    assert user.created_at == now

def test_user_required_fields():
    user = User(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password == "password123"

def test_user_nullable_fields():
    user = User(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    assert user.avatar is None
    assert user.github_id is None
    assert user.discord_id is None

def test_user_created_at_default():
    now = datetime.now(pytz.timezone('Europe/Warsaw'))
    user = User(
        username="testuser",
        email="test@example.com",
        password="password123",
        created_at=now
    )
    
    assert user.created_at is not None
    assert isinstance(user.created_at, datetime)

def test_username_max_length():
    username = "a" * 20
    
    user = User(
        username=username,
        email="test@example.com",
        password="password123"
    )
    
    assert user.username == username
    assert len(user.username) == 20

def test_email_max_length():
    local_part = "a" * 64
    domain = "b" * 255
    email = f"{local_part}@{domain}"
    
    user = User(
        username="testuser",
        email=email,
        password="password123"
    )
    
    assert user.email == email

def test_timezone_aware_created_at():
    now = datetime.now(pytz.timezone('Europe/Warsaw'))
    user = User(
        username="testuser",
        email="test@example.com",
        password="password123",
        created_at=now
    )
    
    assert user.created_at.tzinfo is not None
    assert user.created_at.tzinfo.zone == 'Europe/Warsaw'