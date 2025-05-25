import json

def test_register(client):
    response = client.post(
        "/api/register",
        data=json.dumps({"username": "testuser",
          "email": "testuser@example.com",
          "password": "Password123!",
          "password2": "Password123!"
        }),
        content_type='application/json'
    )
    assert response.status_code in [200, 201, 302]
    data = response.get_json()
    assert data['username'] == "testuser"
    assert data['email'] == "testuser@example.com"
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert 'expire_time' in data
    assert 'refresh_expire_time' in data

def test_login_and_logout(client, user):
    response = client.post(
        "/api/login",
        data=json.dumps({
            "usernameOrEmail": "testuser@example.com",
            "password": "Testuser1.",
            "remember": True
        }),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['username'] == "testuser"
    assert data['email'] == "testuser@example.com"
    assert 'access_token' in data
    assert 'refresh_token' in data

    access_token = data['access_token']
    refresh_token = data['refresh_token']

    response = client.post(
        "/api/logout",
        data=json.dumps({
            "refresh_token": refresh_token
        }),
        headers={'Authorization': f'Bearer {access_token}'},
        content_type='application/json'
    )
    data = response.get_json()
    assert response.status_code == 200
    assert "message" in data