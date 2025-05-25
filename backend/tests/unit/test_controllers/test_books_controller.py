import pytest
from unittest.mock import patch, MagicMock
from controllers.books_controller import get_wishlist_for_user, add_book_to_collection, add_book_to_wishlist, get_books_for_user, get_wishlist_for_user
from main import app

@pytest.fixture
def app_context():
    with app.app_context():
        yield

def test_add_book_to_collection_success(app_context):
    user_id = 1
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "cover": "test.jpg",
        "genres": "Fantasy",
        "publisher": "Test Publisher",
        "date": "2023-01-01",
        "pages": 123,
        "isbn": "9781234567897",
        "desc": "Test description"
    }
    
    with patch('models.book_collection.BookCollection.query') as mock_query, \
         patch('models.db.session.add') as mock_add, \
         patch('models.db.session.commit') as mock_commit:
        
        mock_query.filter_by.return_value.first.return_value = None
        book, error = add_book_to_collection(user_id, book_data)
        
        assert book is not None
        assert error is None
        mock_add.assert_called_once()
        mock_commit.assert_called_once()
        assert book.user_id == user_id
        assert book.title == "Test Book"
        assert book.isbn == "9781234567897"

def test_add_book_to_collection_duplicate(app_context):
    user_id = 1
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "isbn": "9781234567897"
    }
    
    with patch('models.book_collection.BookCollection.query') as mock_query:
        mock_existing_book = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_existing_book
        book, error = add_book_to_collection(user_id, book_data)
        
        assert book is None
        assert "już istnieje w kolekcji" in error

def test_add_book_to_wishlist_success(app_context):
    user_id = 1
    book_data = {
        "title": "Test Wishlist Book",
        "author": "Test Author",
        "cover": "test.jpg",
        "genres": "SciFi",
        "publisher": "Test Publisher",
        "date": "2023-02-02",
        "pages": 234,
        "isbn": "9781234567898",
        "desc": "Test description"
    }
    
    with patch('models.wishlist.WishList.query') as mock_query, \
         patch('models.db.session.add') as mock_add, \
         patch('models.db.session.commit') as mock_commit:
        
        mock_query.filter_by.return_value.first.return_value = None
        book, error = add_book_to_wishlist(user_id, book_data)
        
        assert book is not None
        assert error is None
        mock_add.assert_called_once()
        mock_commit.assert_called_once()
        assert book.user_id == user_id
        assert book.title == "Test Wishlist Book"
        assert book.isbn == "9781234567898"

def test_add_book_to_wishlist_duplicate(app_context):
    user_id = 1
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "isbn": "9781234567897"
    }
    
    with patch('models.wishlist.WishList.query') as mock_query:
        mock_existing_book = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_existing_book
        book, error = add_book_to_wishlist(user_id, book_data)
        
        assert book is None
        assert "już istnieje na liście życzeń" in error

def test_get_books_for_user(app_context):
    user_id = 1
    
    with patch('models.book_collection.BookCollection.query') as mock_query:
        mock_book1 = MagicMock()
        mock_book1.title = "Book 1"
        mock_book2 = MagicMock()
        mock_book2.title = "Book 2"
        mock_query.filter_by.return_value.all.return_value = [mock_book1, mock_book2]
        books = get_books_for_user(user_id)
        
        assert len(books) == 2
        assert books[0].title == "Book 1"
        assert books[1].title == "Book 2"
        mock_query.filter_by.assert_called_once_with(user_id=user_id)

def test_get_wishlist_for_user(app_context):
    user_id = 1
    
    with patch('models.wishlist.WishList.query') as mock_query:
        mock_book1 = MagicMock()
        mock_book1.title = "Wishlist Book 1"
        mock_book2 = MagicMock()
        mock_book2.title = "Wishlist Book 2"
        mock_query.filter_by.return_value.all.return_value = [mock_book1, mock_book2]
        books = get_wishlist_for_user(user_id)
        
        assert len(books) == 2
        assert books[0].title == "Wishlist Book 1"
        assert books[1].title == "Wishlist Book 2"
        mock_query.filter_by.assert_called_once_with(user_id=user_id)

def test_get_books_for_user_empty(app_context):
    user_id = 1
    
    with patch('models.book_collection.BookCollection.query') as mock_query:
        mock_query.filter_by.return_value.all.return_value = []
        books = get_books_for_user(user_id)
        
        assert len(books) == 0
        assert isinstance(books, list)

def test_get_wishlist_for_user_empty(app_context):
    user_id = 1
    
    with patch('models.wishlist.WishList.query') as mock_query:
        mock_query.filter_by.return_value.all.return_value = []
        books = get_wishlist_for_user(user_id)
        
        assert len(books) == 0
        assert isinstance(books, list)