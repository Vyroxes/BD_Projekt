from unittest.mock import patch, MagicMock
from controllers.auth_controller import get_user_by_id, register_user, authenticate_user

def test_register_user_success(app_context):
    with patch('models.User.query') as mock_query, \
         patch('controllers.auth_controller.generate_password_hash') as mock_hash, \
         patch('models.db.session.add') as mock_add, \
         patch('models.db.session.commit') as mock_commit:
        
        mock_query.filter_by.return_value.first.return_value = None
        mock_hash.return_value = b'hashed_password'
        
        result = register_user('newuser', 'password123')
        
        assert result is not None
        assert result.username == 'newuser'
        mock_add.assert_called_once()
        mock_commit.assert_called_once()

def test_register_user_existing_username(app_context):
    with patch('models.User.query') as mock_query:
        mock_existing_user = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_existing_user
        
        result = register_user('existinguser', 'password123')
        
        assert result is None
        
def test_authenticate_user_with_username_success(app_context):
    with patch('models.User.query') as mock_query, \
         patch('controllers.auth_controller.check_password_hash') as mock_check:
        
        mock_user = MagicMock()
        mock_user.username = 'testuser'
        mock_user.password = 'hashed_password'
        
        mock_query.filter.return_value.first.return_value = mock_user
        mock_check.return_value = True
        
        result = authenticate_user('testuser', 'password123')
        
        assert result == mock_user
        mock_check.assert_called_with('hashed_password', 'password123')

def test_authenticate_user_with_email_success(app_context):
    with patch('models.User.query') as mock_query, \
         patch('controllers.auth_controller.check_password_hash') as mock_check:
        
        mock_user = MagicMock()
        mock_user.username = 'testuser'
        mock_user.email = 'test@example.com'
        mock_user.password = 'hashed_password'
        
        mock_query.filter.return_value.first.return_value = mock_user
        mock_check.return_value = True
        
        result = authenticate_user('test@example.com', 'password123')
        
        assert result == mock_user
        mock_check.assert_called_with('hashed_password', 'password123')

def test_authenticate_user_wrong_password(app_context):
    with patch('models.User.query') as mock_query, \
         patch('controllers.auth_controller.check_password_hash') as mock_check:
        
        mock_user = MagicMock()
        mock_user.username = 'testuser'
        mock_user.password = 'hashed_password'
        
        mock_query.filter.return_value.first.return_value = mock_user
        mock_check.return_value = False
        
        result = authenticate_user('testuser', 'wrongpassword')
        
        assert result is None
        mock_check.assert_called_with('hashed_password', 'wrongpassword')

def test_authenticate_user_nonexistent(app_context):
    with patch('models.User.query') as mock_query:
        mock_query.filter.return_value.first.return_value = None
        
        result = authenticate_user('nonexistent', 'password123')
        
        assert result is None

def test_get_user_by_id_found(app_context):
    with patch('models.User.query') as mock_query:
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = 'testuser'
        
        mock_query.get.return_value = mock_user

        result = get_user_by_id(1)
        
        assert result == mock_user
        mock_query.get.assert_called_with(1)

def test_get_user_by_id_not_found(app_context):
    with patch('models.User.query') as mock_query:
        mock_query.get.return_value = None
        
        result = get_user_by_id(999)
        
        assert result is None
        mock_query.get.assert_called_with(999)