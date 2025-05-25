from unittest.mock import patch, MagicMock
from controllers.user_controller import delete_user_and_data, get_user_by_username, get_all_users

def test_get_user_by_username_found(app_context):
    mock_user = MagicMock()
    mock_user.username = "testuser"
    mock_user.email = "test@example.com"
    
    with patch('models.User.query') as mock_query:
        mock_query.filter.return_value.first.return_value = mock_user
        
        result = get_user_by_username("testuser")
        
        assert result == mock_user
        mock_query.filter.assert_called_once()

def test_get_user_by_username_case_insensitive(app_context):
    mock_user = MagicMock()
    mock_user.username = "TestUser"
    mock_user.email = "test@example.com"
    
    with patch('models.User.query') as mock_query:
        mock_query.filter.return_value.first.return_value = mock_user
        
        result = get_user_by_username("testuser")
        
        assert result == mock_user

def test_get_user_by_username_not_found(app_context):
    with patch('models.User.query') as mock_query:
        mock_query.filter.return_value.first.return_value = None
        
        result = get_user_by_username("nonexistent")
        
        assert result is None
        mock_query.filter.assert_called_once()

def test_delete_user_and_data(app_context):
    mock_user = MagicMock()
    mock_user.id = 1
    
    with patch('models.BookCollection.query') as mock_book_query, \
         patch('models.WishList.query') as mock_wishlist_query, \
         patch('models.db.session.delete') as mock_delete, \
         patch('models.db.session.commit') as mock_commit:
        
        mock_book_query.filter_by.return_value.delete.return_value = None
        mock_wishlist_query.filter_by.return_value.delete.return_value = None
        
        delete_user_and_data(mock_user)
        
        mock_book_query.filter_by.assert_called_once_with(user_id=1)
        mock_book_query.filter_by.return_value.delete.assert_called_once()
        
        mock_wishlist_query.filter_by.assert_called_once_with(user_id=1)
        mock_wishlist_query.filter_by.return_value.delete.assert_called_once()
        
        mock_delete.assert_called_once_with(mock_user)
        mock_commit.assert_called_once()

def test_get_all_users(app_context):
    mock_user1 = MagicMock()
    mock_user1.username = "user1"
    mock_user2 = MagicMock()
    mock_user2.username = "user2"
    
    with patch('models.User.query') as mock_query:
        mock_query.all.return_value = [mock_user1, mock_user2]
        
        result = get_all_users()
        
        assert len(result) == 2
        assert result[0].username == "user1"
        assert result[1].username == "user2"
        mock_query.all.assert_called_once()

def test_get_all_users_empty(app_context):
    with patch('models.User.query') as mock_query:
        mock_query.all.return_value = []
        
        result = get_all_users()
        
        assert len(result) == 0
        assert isinstance(result, list)
        mock_query.all.assert_called_once()