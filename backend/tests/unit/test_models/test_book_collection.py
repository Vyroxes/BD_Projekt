from datetime import date
from models.book_collection import BookCollection

def test_create_book_collection():
    book = BookCollection(
        user_id=1,
        title="Test Book",
        author="Test Author",
        cover="https://example.com/cover.jpg",
        genres="Fantasy",
        publisher="Test Publisher",
        date=date(2023, 5, 25),
        pages=300,
        isbn="9781234567897",
        desc="This is a test book description"
    )
    
    assert book.user_id == 1
    assert book.title == "Test Book"
    assert book.author == "Test Author"
    assert book.cover == "https://example.com/cover.jpg"
    assert book.genres == "Fantasy"
    assert book.publisher == "Test Publisher"
    assert book.date == date(2023, 5, 25)
    assert book.pages == 300
    assert book.isbn == "9781234567897"
    assert book.desc == "This is a test book description"
    assert book.rate is None
    assert book.review is None

def test_book_collection_nullable_fields():
    book = BookCollection(
        user_id=1,
        title="Test Book",
        author="Test Author",
        cover="https://example.com/cover.jpg",
        genres="Fantasy",
        publisher="Test Publisher",
        date=date(2023, 5, 25),
        pages=300,
        isbn="9781234567897",
        desc="This is a test book description",
        rate=4.5,
        review="Great book!"
    )
    
    assert book.rate == 4.5
    assert book.review == "Great book!"

def test_book_collection_to_dict():
    book = BookCollection(
        id=1,
        user_id=1,
        title="Test Book",
        author="Test Author",
        cover="https://example.com/cover.jpg",
        genres="Fantasy",
        publisher="Test Publisher",
        date=date(2023, 5, 25),
        pages=300,
        isbn="9781234567897",
        desc="This is a test book description",
        rate=4.5,
        review="Great book!"
    )
    
    book_dict = book.to_dict()
    
    assert book_dict['id'] == 1
    assert book_dict['title'] == "Test Book"
    assert book_dict['author'] == "Test Author"
    assert book_dict['cover'] == "https://example.com/cover.jpg"
    assert book_dict['genres'] == "Fantasy"
    assert book_dict['date'] == "25-05-2023"
    assert book_dict['pages'] == 300
    assert book_dict['rate'] == 4.5
    assert 'publisher' not in book_dict
    assert 'isbn' not in book_dict
    assert 'desc' not in book_dict
    assert 'review' not in book_dict

def test_book_collection_full_to_dict():
    book = BookCollection(
        id=1,
        user_id=1,
        title="Test Book",
        author="Test Author",
        cover="https://example.com/cover.jpg",
        genres="Fantasy",
        publisher="Test Publisher",
        date=date(2023, 5, 25),
        pages=300,
        isbn="9781234567897",
        desc="This is a test book description",
        rate=4.5,
        review="Great book!"
    )
    
    book_dict = book.full_to_dict()
    
    assert book_dict['id'] == 1
    assert book_dict['title'] == "Test Book"
    assert book_dict['author'] == "Test Author"
    assert book_dict['cover'] == "https://example.com/cover.jpg"
    assert book_dict['genres'] == "Fantasy"
    assert book_dict['publisher'] == "Test Publisher"
    assert book_dict['date'] == "25-05-2023"
    assert book_dict['pages'] == 300
    assert book_dict['isbn'] == "9781234567897"
    assert book_dict['desc'] == "This is a test book description"
    assert book_dict['rate'] == 4.5
    assert book_dict['review'] == "Great book!"

def test_book_collection_date_formatting():
    book = BookCollection(
        user_id=1,
        title="Test Book",
        author="Test Author",
        cover="https://example.com/cover.jpg",
        genres="Fantasy",
        publisher="Test Publisher",
        date=date(2023, 12, 31),
        pages=300,
        isbn="9781234567897",
        desc="This is a test book description"
    )
    
    assert book.to_dict()['date'] == "31-12-2023"
    assert book.full_to_dict()['date'] == "31-12-2023"

def test_book_collection_with_null_rate_and_review():
    book = BookCollection(
        id=1,
        user_id=1,
        title="Test Book",
        author="Test Author",
        cover="https://example.com/cover.jpg",
        genres="Fantasy",
        publisher="Test Publisher",
        date=date(2023, 5, 25),
        pages=300,
        isbn="9781234567897",
        desc="This is a test book description"
    )
    
    book_dict = book.to_dict()
    book_full_dict = book.full_to_dict()
    
    assert book_dict['rate'] is None
    assert book_full_dict['rate'] is None
    assert book_full_dict['review'] is None

def test_book_collection_max_page_count():
    book = BookCollection(
        user_id=1,
        title="Test Book",
        author="Test Author",
        cover="https://example.com/cover.jpg",
        genres="Fantasy",
        publisher="Test Publisher",
        date=date(2023, 5, 25),
        pages=9999,
        isbn="9781234567897",
        desc="This is a test book description"
    )
    
    assert book.pages == 9999