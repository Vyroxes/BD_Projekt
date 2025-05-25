import json

def test_book_addition_and_retrieval(client, auth_token):
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
    data = response.get_json()
    assert response.status_code == 201
    assert "message" in data
    
    response = client.get(
        '/api/testuser/bc',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200

def test_edit_book(client, auth_token, book_in_collection):
    response = client.patch(
        f'/api/edit-book/bc/{book_in_collection}',
        data=json.dumps({
            "title": "Updated Book",
            "author": "Updated Author",
            "cover": "updated.jpg",
            "genres": "Mystery",
            "publisher": "Updated Publisher",
            "date": "2023-03-03",
            "pages": 456,
            "isbn": "9781234567890",
            "desc": "Updated description"
        }),
        headers={'Authorization': f'Bearer {auth_token}'},
        content_type='application/json'
    )
    data = response.get_json()
    assert response.status_code == 200
    assert "message" in data
    
    response = client.get(
        f'/api/book-details/bc/{book_in_collection}',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    book_data = response.json
    assert book_data["title"] == "Updated Book"
    assert book_data["author"] == "Updated Author"

def test_review_book(client, auth_token, book_in_collection):
    response = client.patch(
        f'/api/review-book/bc/{book_in_collection}',
        data=json.dumps({
            "rate": 4.5,
            "review": "Great book, would recommend!"
        }),
        headers={'Authorization': f'Bearer {auth_token}'},
        content_type='application/json'
    )
    data = response.get_json()
    assert response.status_code == 200
    assert "message" in data
    
    response = client.get(
        f'/api/book-details/bc/{book_in_collection}',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    book_data = response.json
    assert book_data["rate"] == 4.5
    assert book_data["review"] == "Great book, would recommend!"

def test_get_book_details(client, auth_token, book_in_collection):
    response = client.get(
        f'/api/book-details/bc/{book_in_collection}',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    book_data = response.json
    assert "title" in book_data
    assert "author" in book_data
    assert "genres" in book_data
    assert "publisher" in book_data
    
    response = client.get(
        '/api/book-details/bc/999',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 404

def test_book_exists(client, auth_token, book_in_collection):
    response = client.get(
        f'/api/book-exists/bc/{book_in_collection}',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    assert response.json["exists"] == True
    
    response = client.get(
        '/api/book-exists/bc/999',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    assert response.json["exists"] == False

def test_remove_book(client, auth_token, book_in_collection, user):
    response = client.delete(
        f'/api/remove-book/bc/{book_in_collection}',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    assert response.json["message"] == "Książka usunięta z kolekcji."
    
    response = client.get(
        f'/api/book-details/bc/{book_in_collection}',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 404

def test_remove_all_books(client, auth_token, user):
    client.post(
        '/api/add-book/bc',
        data=json.dumps({
            "title": "Book 1",
            "author": "Author 1",
            "cover": "cover1.jpg",
            "genres": "Fantasy",
            "publisher": "Publisher 1",
            "date": "2023-01-01",
            "pages": 123,
            "isbn": "9781234567897",
            "desc": "Description 1"
        }),
        headers={'Authorization': f'Bearer {auth_token}'},
        content_type='application/json'
    )
    
    client.post(
        '/api/add-book/bc',
        data=json.dumps({
            "title": "Book 2",
            "author": "Author 2",
            "cover": "cover2.jpg",
            "genres": "SciFi",
            "publisher": "Publisher 2",
            "date": "2023-02-02",
            "pages": 234,
            "isbn": "9781234567898",
            "desc": "Description 2"
        }),
        headers={'Authorization': f'Bearer {auth_token}'},
        content_type='application/json'
    )
    
    response = client.delete(
        '/api/remove-all-books/bc',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    assert "Usunięto wszystkie książki" in response.json["message"]
    
    response = client.get(
        f'/api/{user.username}/bc',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    assert response.json == []

def test_move_book(client, auth_token, book_in_collection, book_in_wishlist, user):
    response = client.post(
        f'/api/move-book-to/bc/{book_in_collection}',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    assert response.json["message"] == "Książka przeniesiona na listę życzeń."
    
    response = client.get(
        f'/api/book-details/bc/{book_in_collection}',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 404
    
    response = client.get(
        f'/api/{user.username}/wl',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    books = response.json
    assert len(books) >= 1
    assert any(book.get("title") == "Test Book" for book in books)
    
    response = client.post(
        f'/api/move-book-to/wl/{book_in_wishlist}',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    assert response.json["message"] == "Książka przeniesiona do kolekcji."

def test_invalid_edit_data(client, auth_token, book_in_collection):
    response = client.patch(
        f'/api/edit-book/bc/{book_in_collection}',
        data=json.dumps({
            "title": "Updated Book",
        }),
        headers={'Authorization': f'Bearer {auth_token}'},
        content_type='application/json'
    )
    assert response.status_code == 400
    assert "Brak wymaganego pola" in response.json["error"]
    
    response = client.patch(
        f'/api/edit-book/bc/{book_in_collection}',
        data=json.dumps({
            "title": "",
            "author": "Updated Author",
            "cover": "updated.jpg",
            "genres": "Mystery",
            "publisher": "Updated Publisher",
            "date": "2023-03-03",
            "pages": 456,
            "isbn": "9781234567890",
            "desc": "Updated description"
        }),
        headers={'Authorization': f'Bearer {auth_token}'},
        content_type='application/json'
    )
    assert response.status_code == 400
    assert "nie może być puste" in response.json["error"]
    
    response = client.patch(
        f'/api/edit-book/bc/{book_in_collection}',
        data=json.dumps({
            "title": "Updated Book",
            "author": "Updated Author",
            "cover": "updated.jpg",
            "genres": "Mystery",
            "publisher": "Updated Publisher",
            "date": "invalid-date",
            "pages": 456,
            "isbn": "9781234567890",
            "desc": "Updated description"
        }),
        headers={'Authorization': f'Bearer {auth_token}'},
        content_type='application/json'
    )
    assert response.status_code == 400