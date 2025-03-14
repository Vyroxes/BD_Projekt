import React, { useEffect, useState } from 'react';
import useIsAuthenticated from 'react-auth-kit/hooks/useIsAuthenticated'
import useAuthHeader from 'react-auth-kit/hooks/useAuthHeader'
import { useNavigate } from "react-router-dom";
import { Card, CardMedia, CardContent, Typography } from '@mui/material';
import axios from 'axios';

import './BookCollection.css';

const BookCollection = () =>
{
    const isAuthenticated = useIsAuthenticated();
    const authHeader = useAuthHeader();
    const navigate = useNavigate();
    const [books, setBooks] = useState([]);
    
    useEffect(() => 
    {
        if (!isAuthenticated) 
        {
            navigate('/login');
        }
        else
        {
            fetchBooks();
        }
    }, [isAuthenticated, navigate]);

    const fetchBooks = async () => 
    {
        try 
        {
            const response = await axios.get('http://localhost:5000/book-collection', {
                headers: {
                    'Authorization': authHeader
                },
                withCredentials: true
            });

            setBooks(response.data);
        } 
        catch (error) 
        {
            console.error('Błąd podczas ładowania książek w kolekcji: ', error);
        }
    };

    return (
        <div className='book-collection-container'>
            {books.map(book => (
                <div key={book.id} className="book-card">
                    <img
                        src={book.cover}
                        alt={book.title}
                        onError={(e) => {
                            e.target.onerror = null;
                            e.target.src = "unknown.jpg";
                        }}
                        loading="lazy"
                    />
                    <p className="book-card-title">{book.id}. {book.title}</p>
                    <p className="book-card-author">{book.author}</p>
                </div>
                // <Card key={book.id}>
                //     <CardMedia
                //         component="img"
                //         image={book.cover}
                //         alt={book.title}
                //         onError={(e) => e.target.src = '/public/unknown.jpg'} 
                //     />
                //     <CardContent>
                //         <Typography>
                //             {book.title}
                //         </Typography>
                //         <Typography>
                //             {book.author}
                //         </Typography>
                //     </CardContent>
                // </Card>
            ))}
        </div>
    );
};

export default BookCollection;