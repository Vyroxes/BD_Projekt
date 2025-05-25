from unittest.mock import patch, mock_open

def test_contact_success(client):
    mocked_open = mock_open(read_data="1. 01-01-2025 12:00:00\nNazwa użytkownika: user1\n")
    
    with patch('builtins.open', mocked_open):
        response = client.post(
            '/api/contact',
            json={
                'username': 'testuser',
                'email': 'test@example.com',
                'subject': 'Test Subject',
                'text': 'This is a test message.'
            }
        )
        
        assert response.status_code == 200
        assert response.json['message'] == 'Wiadomość została wysłana.'
        
        assert mocked_open.call_count >= 2

def test_contact_missing_fields(client):
    response = client.post(
        '/api/contact',
        json={
            'username': 'testuser',
            'email': 'test@example.com',
        }
    )
    
    assert response.status_code == 400
    assert 'Wszystkie pola są wymagane' in response.json['error']

def test_contact_first_message(client):
    def mock_open_side_effect(file_name, mode, *args, **kwargs):
        mock = mock_open()
        if file_name == "contact.txt" and mode == "r":
            raise FileNotFoundError
        return mock.return_value
    
    with patch('builtins.open', side_effect=mock_open_side_effect):
        response = client.post(
            '/api/contact',
            json={
                'username': 'testuser',
                'email': 'test@example.com',
                'subject': 'First Message',
                'text': 'This is the first message.'
            }
        )
        
        assert response.status_code == 200
        assert response.json['message'] == 'Wiadomość została wysłana.'