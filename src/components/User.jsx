import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { authAxios, clearTokens, getCookie } from '../utils/Auth';

import './User.css';

const User = () => {
    const [loading, setLoading] = useState(true);
    const [email, setEmail] = useState(null); 
    const [avatarUrl, setAvatarUrl] = useState(null);
    const [bookStats, setBookStats] = useState({
        collectionCount: 0,
        wishlistCount: 0,
        totalPages: 0,
    });

    const { username } = useParams();

    const navigate = useNavigate();
    const currentUsername = getCookie('username');
    const adminUsername = import.meta.env.VITE_ADMIN_USERNAME;

    useEffect(() => {
        if (username) {
            fetchUserData();
        }
    }, [username]);

    const fetchUserData = async () => {
        try {
            const response = await authAxios.get(`/api/user/${username}`);
            if (response.status === 200) {
                setEmail(response.data.email);
                setAvatarUrl(response.data.avatar_url);
                fetchBookStats();
            } else {
                navigate('/home');
            }
        } catch (error) {
            console.error("Błąd podczas pobierania danych użytkownika: ", error);
            navigate('/home');
        }
    };
    
    const fetchBookStats = async () => {
        try {
            const collectionResponse = await authAxios.get(`/api/${username}/bc`);
            const wishlistResponse = await authAxios.get(`/api/${username}/wl`);

            const collectionCount = collectionResponse.data.length;
            const wishlistCount = wishlistResponse.data.length;
            const totalPages = collectionResponse.data.reduce((sum, book) => sum + book.pages, 0) +
                                wishlistResponse.data.reduce((sum, book) => sum + book.pages, 0);

            setBookStats({
                collectionCount,
                wishlistCount,
                totalPages,
            });
            setLoading(false);
        } catch (error) {
            console.error("Błąd podczas pobierania statystyk książek: ", error);
        }
    };

    const deleteAccount = async () => {
        const confirmDelete = window.confirm("Czy na pewno chcesz usunąć konto?");
        
        if (!confirmDelete) {
            return;
        }
        try {
            const response = await authAxios.delete(`/api/delete-account/${username}`);
            if (response.status === 200) {
                console.log("Usunięto konto pomyślnie");
                clearTokens();
                navigate('/login');
            }
        }
        catch (error) {
            console.error("Błąd podczas usuwania konta: ", error);
        }
    };

    if(loading) {
        return;
    }

    return (
        <div className="user-container">
            <h1>Profil użytkownika</h1>
            <div className="user-header">
                    <img
                    src={avatarUrl || "/unknown_avatar.jpg"}
                    alt={username}
                    className="user-avatar"
                    onError={(e) => {
                        e.target.onerror = null;
                        e.target.src = "/unknown_avatar.jpg";
                    }}
                    loading="lazy"
                    />
                <h1>{username}</h1>
                <a>{email}</a>
            </div>
            <div className="user-stats">
                <h2>Statystyki</h2>
                    <li>Książki w kolekcji: {bookStats.collectionCount}</li>
                    <li>Książki na liście życzeń: {bookStats.wishlistCount}</li>
                    <li>Łączna liczba stron: {bookStats.totalPages}</li>
            </div>
            <div className="user-actions">
                {username !== currentUsername && (<button onClick={() => navigate('/users')}>Powrót</button>)}
                {(username === currentUsername || currentUsername === adminUsername) && (<button className='delete-account-button' onClick={() => deleteAccount()}>Usuń konto</button>)}
            </div>
        </div>
    );
};

export default User;