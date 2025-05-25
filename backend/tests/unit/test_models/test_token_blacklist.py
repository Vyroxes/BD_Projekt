from datetime import datetime, timedelta
from models.token_blacklist import TokenBlacklist

def test_create_token_blacklist():
    now = datetime.now()
    token_blacklist = TokenBlacklist(
        username="testuser",
        email="test@example.com",
        jti="12345678-1234-5678-1234-567812345678",
        expires_at=now
    )
    
    assert token_blacklist.username == "testuser"
    assert token_blacklist.email == "test@example.com"
    assert token_blacklist.jti == "12345678-1234-5678-1234-567812345678"
    assert token_blacklist.expires_at == now

def test_token_blacklist_required_fields():
    token_blacklist = TokenBlacklist(
        username="testuser",
        email="test@example.com",
        jti="12345678-1234-5678-1234-567812345678",
        expires_at=datetime.now()
    )
    
    assert token_blacklist.username is not None
    assert token_blacklist.email is not None
    assert token_blacklist.jti is not None
    assert token_blacklist.expires_at is not None

def test_token_blacklist_jti_format():
    token = TokenBlacklist(
        username="testuser",
        email="test@example.com",
        jti="12345678-1234-5678-1234-567812345678",
        expires_at=datetime.now()
    )
    
    assert len(token.jti) == 36
    assert token.jti.count('-') == 4

def test_token_blacklist_with_future_expiration():
    now = datetime.now()
    future = now + timedelta(days=7)
    
    token = TokenBlacklist(
        username="testuser",
        email="test@example.com",
        jti="12345678-1234-5678-1234-567812345678",
        expires_at=future
    )
    
    assert token.expires_at > now
    assert (token.expires_at - now).days == 7

def test_token_blacklist_username_max_length():
    username = "a" * 20
    
    token = TokenBlacklist(
        username=username,
        email="test@example.com",
        jti="12345678-1234-5678-1234-567812345678",
        expires_at=datetime.now()
    )
    
    assert token.username == username
    assert len(token.username) == 20

def test_token_blacklist_email_max_length():
    local_part = "a" * 64
    domain = "b" * 255
    email = f"{local_part}@{domain}"
    
    token = TokenBlacklist(
        username="testuser",
        email=email,
        jti="12345678-1234-5678-1234-567812345678",
        expires_at=datetime.now()
    )
    
    assert token.email == email