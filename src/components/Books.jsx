import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from "react-router-dom";
import DoubleRangeSlider from "./DoubleRangeSlider";
import { IoMdClose } from "react-icons/io";
import { authAxios } from '../utils/Auth';

import './Books.css';

const Books = () =>
{
    const navigate = useNavigate();
    const location = useLocation();
    
    const [books, setBooks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");
    const [sortMethod, setSortMethod] = useState("idAsc");
    const [filterVisible, setFilterVisible] = useState(false);

    const isDisabled = search.trim() === "";

    const [filterCriteria, setFilterCriteria] = useState({
        genres: {},
        minPages: 0,
        maxPages: 0,
        minYear: 0,
        maxYear: 0,
    });

    const [initialBounds, setInitialBounds] = useState({
        genres: {},
        minPages: 0,
        maxPages: 0,
        minYear: 0,
        maxYear: 0,
    });

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

    const sortLabels = {
        idAsc: "Data dodania ↑",
        idDesc: "Data dodania ↓",
        titleAsc: "Tytuł ↑",
        titleDesc: "Tytuł ↓",
        authorAsc: "Autor ↑",
        authorDesc: "Autor ↓",
        dateAsc: "Data wydania ↑",
        dateDesc: "Data wydania ↓",
        pagesAsc: "Liczba stron ↑",
        pagesDesc: "Liczba stron ↓",
        rateAsc: "Ocena ↑",
        rateDesc: "Ocena ↓"
    };

    const sortMethods = [
        "idAsc", "idDesc",
        "titleAsc", "titleDesc",
        "authorAsc", "authorDesc",
        "dateAsc", "dateDesc",
        "pagesAsc", "pagesDesc",
        "rateAsc", "rateDesc"
    ];
    
    useEffect(() => {
        fetchBooks();
    }, []);

    const fetchBooks = async () => 
    {
        try 
        {
            let response;

            if(location.pathname === "/book-collection")
            {
                response = await authAxios.get('/api/book-collection');
            }
            else if(location.pathname === "/wish-list")
            {
                response = await authAxios.get('/api/wish-list');
            }

            if (response.status == 200) {
                setBooks(response.data);

                const minPages = Math.min(...response.data.map(b => b.pages));
                const maxPages = Math.max(...response.data.map(b => b.pages));
                const minYear = Math.min(...response.data.map(b => {
                    const dateParts = b.date.split('-');
                    return parseInt(dateParts[2]);
                }));
                const maxYear = Math.max(...response.data.map(b => {
                    const dateParts = b.date.split('-');
                    return parseInt(dateParts[2]);
                }));

                const calculatedBounds = { minPages, maxPages, minYear, maxYear };
                setInitialBounds({ ...calculatedBounds, genres: {} });
                setFilterCriteria({
                    genres: filterCriteria.genres,
                    minPages,
                    maxPages,
                    minYear,
                    maxYear
                });

                setLoading(false);
            }
        } 
        catch (error) 
        {
            console.error('Błąd podczas ładowania książek w kolekcji/na liście życzeń: ', error);
        }
    };

    const handleSortClick = () => 
    {
        const currentIndex = sortMethods.indexOf(sortMethod);
        const nextIndex = (currentIndex + 1) % sortMethods.length;
        setSortMethod(sortMethods[nextIndex]);
    };

    const filteredBooks = books
    .filter(book => {
        const matchesSearch = book.title?.toLowerCase().includes(search.toLowerCase()) || book.author?.toLowerCase().includes(search.toLowerCase());
        
        const bookGenres = book.genres.toLowerCase().split(', ').map(g => g.trim());
        const selectedGenres = Object.keys(filterCriteria.genres).filter(g => filterCriteria.genres[g]);
        const genreMatch = selectedGenres.length === 0 || selectedGenres.every(g => bookGenres.includes(g));
        
        const pagesMatch = book.pages >= filterCriteria.minPages && book.pages <= filterCriteria.maxPages;

        const dateParts = book.date.split('-');
        const yearMatch = parseInt(dateParts[2]) >= filterCriteria.minYear && parseInt(dateParts[2]) <= filterCriteria.maxYear;

        return matchesSearch && genreMatch && pagesMatch && yearMatch;
    })
    .sort((a, b) => {
        switch (sortMethod) {
            case 'idAsc':
                return a.id - b.id;
            case 'idDesc':
                return b.id - a.id;
            case 'titleAsc':
                return a.title.localeCompare(b.title);
            case 'titleDesc':
                return b.title.localeCompare(a.title);
            case 'authorAsc':
                return a.author.localeCompare(b.author);
            case 'authorDesc':
                return b.author.localeCompare(a.author);
            case 'dateAsc':
                return new Date(a.date.split('-').reverse().join('-')) - new Date(b.date.split('-').reverse().join('-'));
            case 'dateDesc':
                return new Date(b.date.split('-').reverse().join('-')) - new Date(a.date.split('-').reverse().join('-'));
            case 'pagesAsc':
                return a.pages - b.pages;
            case 'pagesDesc':
                return b.pages - a.pages;
            case 'rateAsc':
                return a.rate - b.rate;
            case 'rateDesc':
                return b.rate - a.rate;
            default:
                return 0;
        }
    });

    const removeAllBooks = async () => {
        try {
            let response;

            if (location.pathname.startsWith("/book-collection")) {
                response = await authAxios.delete(`/api/bc-remove-all-books`);
            } else if (location.pathname.startsWith("/wish-list")) {
                response = await authAxios.delete(`/api/wl-remove-all-books`);
            }

            if (response.status === 200) {
                fetchBooks();
            }
        } catch (error) {
            console.error('Błąd podczas usuwania książki: ', error);
        }
    };

    if(loading) {
        return;
    }

    return (
        <div className='book-collection'>
            <div className='book-collection-bar'>
            <div className='book-collection-bar-container1'>
                </div>
                <div className='book-collection-bar-container2'>
                    <button onClick={handleSortClick}>
                        Sortuj ({sortLabels[sortMethod]})
                    </button>
                </div>
                <div className='book-collection-bar-container3'>
                    <input
                        type="text"
                        id="search"
                        name="search"
                        placeholder="Tytuł lub autor książki"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                    <div>
                        <button
                            className="book-collection-search-button"
                            type="button"
                            disabled={isDisabled}
                            onClick={() => setSearch("")}
                        >
                            <IoMdClose/>
                        </button>
                    </div>
                </div>
                <div className='book-collection-bar-container4'>
                    <button onClick={() => setFilterVisible((prevState) => !prevState)}>
                        Filtruj
                    </button>
                    <button onClick={() => removeAllBooks()}>Usuń wszystko</button>
                </div>
                <div className='book-collection-bar-container5'>
                    <button onClick={() => {
                        if(location.pathname === "/book-collection") {
                            navigate("/bc-add-book")
                        } else if(location.pathname === "/wish-list") {
                            navigate("/wl-add-book")
                        }
                    }}>
                        Dodaj
                    </button>
                </div>
            </div>
            {filterVisible && (
            <div className="book-collection-filter">
                <div className="book-collection-filter-genres">
                    <h3>Gatunki</h3>
                    {genresList.map((genre) => (
                        <label key={genre}>
                        <input
                            type="checkbox"
                            checked={filterCriteria.genres[genre] || false}
                            onChange={(e) =>
                            setFilterCriteria({
                                ...filterCriteria,
                                genres: {
                                ...filterCriteria.genres,
                                [genre]: e.target.checked,
                                },
                            })
                            }
                        />
                        {genre}
                        </label>
                    ))}
                </div>
                    <div className="book-collection-filter-controls">
                    <h3>Liczba stron</h3>
                    <DoubleRangeSlider
                        initialBounds={initialBounds}
                        filterCriteria={filterCriteria}
                        setFilterCriteria={setFilterCriteria}
                    />
                    </div>
                <div className="book-collection-filter-controls">
                    <h3>Rok wydania</h3>
                    <DoubleRangeSlider
                        initialBounds={{ minPages: initialBounds.minYear, maxPages: initialBounds.maxYear }}
                        filterCriteria={{ minPages: filterCriteria.minYear, maxPages: filterCriteria.maxYear }}
                        setFilterCriteria={(newValues) =>
                        setFilterCriteria({
                            ...filterCriteria,
                            minYear: newValues.minPages,
                            maxYear: newValues.maxPages
                        })
                        }
                    />
                </div>
                <div className="book-collection-filter-button">
                    <button onClick={() => setFilterCriteria(initialBounds)}>Resetuj</button>
                </div>
            </div>
            )}
            <div className='book-collection-container'>
                {filteredBooks.length > 0 ? (
                    filteredBooks.map(book => (
                        <div key={book.id} className="book-card" onClick={() => {
                                if(location.pathname === "/book-collection")
                                {
                                    navigate(`/bc-book-details/${book.id}`);
                                }
                                else if(location.pathname === "/wish-list")
                                {
                                    navigate(`/wl-book-details/${book.id}`);
                                }
                            }}>
                            <img
                                src={book.cover || "/unknown.jpg"}
                                alt={book.title}
                                onError={(e) => {
                                    e.target.onerror = null;
                                    e.target.src = "/unknown.jpg";
                                }}
                                loading="lazy"
                            />
                            <p className="book-card-title">{book.id}. {book.title}</p>
                            <p className="book-card-author">{book.author}</p>
                        </div>
                    ))
                ) : (
                    location.pathname === "/book-collection" ? (
                        <h3 className="no-books">Brak książek w kolekcji</h3>
                    ) : location.pathname === "/wish-list" ? (
                        <h3 className="no-books">Brak książek na liście życzeń</h3>
                    ) : null
                )}
            </div>
        </div>
    );
};

export default Books;