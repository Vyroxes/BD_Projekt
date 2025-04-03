import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from "react-router-dom";
import { authAxios } from '../utils/Auth';

import './AddBook.css';

const AddBook = () =>
{
    const navigate = useNavigate();
    const location = useLocation();
    const [addBookMethod, setAddBookMethod] = useState("");
    const [showCover, setShowCover] = useState(false);
    const [checkedList, setCheckedList] = useState([]);

    const [jsonFileContent, setJsonFileContent] = useState(null);
    const [isbn, setISBN] = useState("");
    const [cover, setCover] = useState("");
    const [title, setTitle] = useState("");
    const [author, setAuthor] = useState("");
    const [genres, setGenres] = useState("");
    const [publisher, setPublisher] = useState("");
    const [date, setDate] = useState("");
    const [pages, setPages] = useState("");
    const [desc, setDesc] = useState("");

    const genresList = [
        "fantasy",
        "science-fiction",
        "horror",
        "romans",
        "thriller",
        "kryminał",
        "historia",
        "poradnik",
        "dla dzieci",
        "dla młodzieży",
        "komiks",
        "manga",
        "na podstawie gry",
        "lektura",
        "beletrystyka",
        "poezja",
        "erotyczne",
        "literatura piękna",
        "przygoda",
        "sensacja",
        "biografia i reportaż",
        "popularnonaukowe",
    ];

    useEffect(() => 
    {
        setGenres(checkedList.sort((a, b) => genresList.indexOf(a) - genresList.indexOf(b)).join(", "));
    }, [checkedList]);

    const handleFileUpload = (file) =>
    {
        if (!file) return;

        if (file.size > 5 * 1024 * 1024) {
            alert("Plik jest za duży. Maksymalny rozmiar to 5 MB.");
            return;
        }

        const reader = new FileReader();
        reader.onloadend = () => {
            setCover(reader.result);
        };

        reader.onerror = () => {
            console.error("Błąd podczas odczytu pliku: ", error);
            alert("Wystąpił problem z odczytem pliku.");
        };

        reader.readAsDataURL(file);
    };

    const handleJsonFileSelect = (file) => {
        if (!file) {
            setJsonFileContent(null);
            return;
        }
    
        const reader = new FileReader();
        reader.onload = () => {
            try {
                setJsonFileContent(reader.result);
            } catch (error) {
                console.error("Błąd podczas odczytywania pliku JSON: ", error);
                alert("Wystąpił problem z odczytem pliku JSON.");
                setJsonFileContent(null);
            }
        };
    
        reader.onerror = () => {
            console.error("Błąd podczas odczytu pliku JSON.");
            alert("Wystąpił problem z odczytem pliku JSON.");
            setJsonFileContent(null);
        };
    
        reader.readAsText(file);
    };

    const processJsonFile = async () => {
        if (!jsonFileContent) {
            alert("Najpierw wybierz plik JSON.");
            return;
        }

        try {
            const jsonData = JSON.parse(jsonFileContent);
            
            if (jsonData["book-collection"] || jsonData["wish-list"]) {
                const booksToAdd = [];

                if (location.pathname === "/bc-add-book" && jsonData["book-collection"]) {
                    jsonData["book-collection"].forEach((book) => {
                        booksToAdd.push({
                            title: book.title || "",
                            author: book.author || "",
                            cover: book.cover || "",
                            genres: book.genres || "",
                            publisher: book.publisher || "",
                            date: book.date || "",
                            pages: book.pages || "",
                            isbn: book.isbn || "",
                            desc: book.desc || "",
                        });
                    });
                } else if (location.pathname === "/wl-add-book" && jsonData["wish-list"]) {
                    jsonData["wish-list"].forEach((book) => {
                        booksToAdd.push({
                            title: book.title || "",
                            author: book.author || "",
                            cover: book.cover || "",
                            genres: book.genres || "",
                            publisher: book.publisher || "",
                            date: book.date || "",
                            pages: book.pages || "",
                            isbn: book.isbn || "",
                            desc: book.desc || "",
                        });
                    });
                }

                if (booksToAdd.length > 0) {
                    let addedCount = 0;
                    let bookCount = booksToAdd.length;
                    for (const book of booksToAdd) {
                        let response;
                        try {
                            response = await onSubmit(book);

                            if (response.status === 201) {
                                addedCount++;
                            }
                            else {
                                bookCount--;
                            }
                        } catch (error) {
                            console.error(`Błąd podczas dodawania książki "${book.title}": `, error);
                        }
                    }
                    
                    if (addedCount === bookCount) {
                        if (location.pathname === "/bc-add-book") {
                            navigate('/book-collection');
                        } else if (location.pathname === "/wl-add-book") {
                            navigate('/wish-list');
                        }
                    } else {
                        alert("Nie udało się dodać żadnej książki.");
                    }
                } else {
                    alert("Nie znaleziono odpowiednich danych dla tej sekcji.");
                }
            } else {
                alert("Nieprawidłowy format pliku JSON.");
            }
        } catch (error) {
            console.error("Błąd podczas parsowania pliku JSON: ", error);
            alert("Nieprawidłowy format pliku JSON.");
        }
    };

    const handleCheckISBN = async () => {
        if (!isbn) {
            alert("Pole z kodem ISBN musi być wypełnione!");
            return;
        }

        const bookData = await fetchBookByISBN(isbn);
        if (bookData) {
            setTitle(bookData.title);
            setAuthor(bookData.author);
            setCover(bookData.cover);
            setPublisher(bookData.publisher);
            setDate(bookData.date);
            setPages(bookData.pages);
            setDesc(bookData.desc);
        }
    };

    const fetchBookByISBN = async (isbn) => {
        try {
            const response = await fetch(
            `https://www.googleapis.com/books/v1/volumes?q=isbn:${isbn}`,
            );
            const data = await response.json();

            if (data.items && data.items.length > 0) {
                const book = data.items[0].volumeInfo;
                return {
                    title: book.title || "",
                    author: book.authors ? book.authors.join(", ") : "",
                    cover: book.imageLinks ? book.imageLinks.thumbnail : "unknown.jpg",
                    publisher: book.publisher || "",
                    date: book.publishedDate || "",
                    pages: book.pageCount || "",
                    desc: book.description || "",
                };
            } else {
                alert("Nie znaleziono książki o tym kodzie ISBN.");
                return null;
            }
        } catch (error) {
            console.error("Błąd podczas pobierania danych książki: ", error);
            alert("Wystąpił błąd podczas pobierania danych książki.");
            return null;
        }
    };

    const onSubmit = async (book) => {
        try {
            let response;

            if(location.pathname === "/bc-add-book")
            {
                if (book) {
                    response = await authAxios.post("/api/bc-add-book", book, {
                        withCredentials: true
                    });
                }
                else {
                    response = await authAxios.post("/api/bc-add-book", {
                        title,
                        author,
                        cover,
                        genres,
                        publisher,
                        date,
                        pages,
                        isbn,
                        desc,
                    }, 
                    {
                        withCredentials: true
                    });
                }
            }
            else if (location.pathname === "/wl-add-book")
            {
                if (book) {
                    response = await authAxios.post("/api/wl-add-book", book, {
                        withCredentials: true
                    });
                }
                else {
                    response = await authAxios.post("/api/wl-add-book", {
                        title,
                        author,
                        cover,
                        genres,
                        publisher,
                        date,
                        pages,
                        isbn,
                        desc,
                    }, 
                    {
                        withCredentials: true
                    });
                }
                
            }
            
            if (response.status == 201)
            {
                if(addBookMethod !== "json")
                {
                    if(location.pathname === "/bc-add-book")
                    {
                        navigate('/book-collection');
                    }
                    else if(location.pathname === "/wl-add-book")
                    {
                        navigate('/wish-list');
                    }
                }
            }
        } catch (error) {
            console.error("Błąd podczas dodawania książki: ", error);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        await onSubmit();
    };

    const handleGenreChange = (event) => 
    {
        const { checked, value } = event.target;
    
        setCheckedList((prev) => 
        {
            if (checked) 
            {
                return [...prev, value];
            } 
            else 
            {
                return prev.filter((genre) => genre !== value);
            }
        });
    };

    return (
        <div>
            {addBookMethod === "" && (
                <div className='add-book-method-container'>
                    <h3>Wybierz metodę dodawania książki</h3>
                    <div className='add-book-method-buttons'>
                        <button onClick={() => setAddBookMethod("manual")}>
                            Manualnie
                        </button>
                        <button onClick={() => setAddBookMethod("isbn")}>
                            Za pomocą ISBN
                        </button>
                        <button onClick={() => setAddBookMethod("json")}>
                            Z pliku JSON
                        </button>
                        <button onClick={() =>
                        {
                            if(location.pathname === "/bc-add-book")
                            {
                                navigate("/book-collection");
                            }
                            else if(location.pathname === "/wl-add-book")
                            {
                                navigate("/wish-list");
                            }
                        }}>
                            Anuluj
                        </button>
                    </div>
                </div>
            )}
            {addBookMethod !== "" && (
                <div className="add-book-container">
                    <div className="add-book-form">
                        <h2>Dodaj książkę</h2>
                        <form onSubmit={handleSubmit}>
                            {addBookMethod === "json" && (
                                <>
                                    <div className="add-book-row">
                                        <label>
                                            JSON (wybierz plik):
                                            <input
                                                type="file"
                                                id='file'
                                                name='file'
                                                accept="application/json"
                                                onChange={(e) => handleJsonFileSelect(e.target.files[0])}
                                            />
                                        </label>
                                    </div>
                                    <div className="add-book-buttons2">
                                        <button type="button" onClick={processJsonFile}>Dodaj książkę</button>
                                        <button type="button" onClick={() => {setAddBookMethod("")}}>
                                            Anuluj
                                        </button>
                                    </div>
                                </>
                            )}
                            {addBookMethod === "isbn" && (
                                <div className="add-book-row">
                                    <label>
                                        ISBN:
                                        <input
                                            type="number"
                                            id='isbn'
                                            name='isbn'
                                            value={isbn}
                                            onChange={(e) => { setISBN(e.target.value) }}
                                            required
                                            min={1000000000000}
                                            max={9999999999999}
                                        />
                                    </label>
                                    <button type="button" onClick={handleCheckISBN}>Sprawdź</button>
                                </div>
                            )}
                            {(addBookMethod === "manual" || addBookMethod === "isbn") && (
                                <>
                                    <div className="add-book-row">
                                        <label>
                                            Okładka (URL):
                                            <input
                                                type="text"
                                                id="cover"
                                                name='cover'
                                                value={cover}
                                                onChange={(e) => setCover(e.target.value)}
                                            />
                                        </label>
                                        <label>
                                            Okładka (wybierz plik):
                                            <input
                                                type="file"
                                                id='file'
                                                name='file'
                                                accept="image/*"
                                                onChange={(e) => handleFileUpload(e.target.files[0])}
                                            />
                                        </label>
                                        <button type="button" onClick={() => setShowCover(!showCover)}>
                                            {showCover ? "Ukryj podgląd okładki" : "Pokaż podgląd okładki"}
                                        </button>
                                    </div>
                                    {showCover && (
                                        <div className="add-book-cover">
                                            <img src={cover || "unknown.jpg"} alt="Podgląd okładki" style={{ maxWidth: "350px", maxHeight: "500px" }} />
                                        </div>
                                    )}
                                    <div className="add-book-row">
                                        <label>
                                            Tytuł:
                                            <input
                                                type="text"
                                                id='title'
                                                name='title'
                                                value={title}
                                                onChange={(e) => setTitle(e.target.value)}
                                                required
                                                minLength="2"
                                                maxLength="100"
                                            />
                                        </label>
                                        <label>
                                            Autor:
                                            <input
                                                type="text"
                                                id='author'
                                                name='author'
                                                value={author}
                                                onChange={(e) => setAuthor(e.target.value)}
                                                required
                                                minLength="5"
                                                maxLength="100"
                                            />
                                        </label>
                                    </div>
                                    <div className="add-book-row-genres">
                                        <a>Gatunki:</a>
                                        {genresList.map((genre) => (
                                            <label key={genre}>
                                                <input
                                                    type="checkbox"
                                                    id={genre}
                                                    name={genre}
                                                    value={genre}
                                                    checked={checkedList.includes(genre)}
                                                    onChange={handleGenreChange}
                                                />
                                                {genre}
                                            </label>
                                        ))}
                                    </div>
                                    <div className="add-book-row">
                                        <label>
                                            Wydawnictwo:
                                            <input
                                                type="text"
                                                id='publisher'
                                                name='publisher'
                                                value={publisher}
                                                onChange={(e) => setPublisher(e.target.value)}
                                                required
                                                minLength="5"
                                                maxLength="100"
                                            />
                                        </label>
                                    </div>
                                    <div className="add-book-row">
                                        <label>
                                            Data wydania:
                                            <input
                                                type="date"
                                                id='date'
                                                name='date'
                                                value={date}
                                                onChange={(e) => setDate(e.target.value)}
                                                required
                                            />
                                        </label>
                                        <label>
                                            Liczba stron:
                                            <input
                                                type="number"
                                                id='pages'
                                                name='pages'
                                                value={pages}
                                                onChange={(e) => setPages(e.target.value)}
                                                required
                                                min={1}
                                                max={9999}
                                            />
                                        </label>
                                    </div>
                                    {addBookMethod === "manual" && (
                                        <div className="add-book-row">
                                            <label>
                                                ISBN:
                                                <input
                                                    type="number"
                                                    id='isbn'
                                                    name='isbn'
                                                    value={isbn}
                                                    onChange={(e) => setISBN(e.target.value)}
                                                    required
                                                    min={1000000000000}
                                                    max={9999999999999}
                                                />
                                            </label>
                                        </div>
                                    )}  
                                    <div className="add-book-row">
                                        <a>Opis:</a>
                                        <textarea
                                            type="text"
                                            id='desc'
                                            name='desc'
                                            value={desc}
                                            onChange={(e) => setDesc(e.target.value)}
                                            required
                                            minLength="1"
                                            maxLength="5000"
                                        />
                                    </div>
                                    <div className="add-book-buttons">
                                        <button type="submit">Dodaj książkę</button>
                                        <button type="button" onClick={() => {setAddBookMethod("")}}>
                                            Anuluj
                                        </button>
                                    </div>
                                </>
                            )}
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AddBook;