import React, { useEffect, useState } from 'react';
import { CiLogout } from "react-icons/ci";
import { useNavigate, useLocation } from "react-router-dom";
import { getCookie, clearTokens, authAxios } from '../utils/Auth';

import './Header.css';

const Header = () => {
    const [avatarUrl, setAvatarUrl] = useState(null);

    const username = getCookie("username");
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        const fetchAvatar = async () => {
            if (username) {
                try {
                    const response = await authAxios.get(`/api/user/${username}`);
                    if (response.status === 200) {
                        setAvatarUrl(response.data.avatar_url);
                    }
                } catch (error) {
                    console.error("Błąd podczas pobierania avatara: ", error);
                }
            }
        };

        fetchAvatar();
    }, [username]);

    const handleLogout = async () => {
        try {
            const response = await authAxios.post("/api/logout", {
                refresh_token: getCookie("refresh_token")
            });
            
            await authAxios.get("/api/clear-session");

            if (response.status === 200) {
                console.log("Wylogowano pomyślnie");
                clearTokens();
                navigate('/login');
            }
        } catch (error) {
            console.error("Błąd podczas wylogowania: ", error);
        }
    };

    return (
        <header className="header">
            <nav className="nav">
                <ul>
                    <li className={location.pathname === "/home" ? "active" : ""}>
                        <a href="/home">STRONA GŁÓWNA</a>
                    </li>
                    <li className={location.pathname === "/book-collection" ? "active" : ""}>
                        <a href="/book-collection">KOLEKCJA KSIĄŻEK</a>
                    </li>
                    <li className={location.pathname === "/wish-list" ? "active" : ""}>
                        <a href="/wish-list">LISTA ŻYCZEŃ</a>
                    </li>
                    <li className={location.pathname === "/premium" ? "active" : ""}>
                        <a href="/premium">PREMIUM</a>
                    </li>
                    <li className={location.pathname === "/contact" ? "active" : ""}>
                        <a href="/contact">KONTAKT</a>
                    </li>
                    <li className={location.pathname === "/users" ? "active" : ""}>
                        <a href="/users">UŻYTKOWNICY</a>
                    </li>
                    <li className={location.pathname === `/users/${username}` ? "active" : ""}>
                        <a href={`/users/${username}`}>
                            <img
                                src={avatarUrl || "/unknown_avatar.jpg"}
                                alt={username}
                                className="avatar"
                                onError={(e) => {
                                    e.target.onerror = null;
                                    e.target.src = "/unknown_avatar.jpg";
                                }}
                                loading="lazy"
                            />
                            {username}
                        </a>
                    </li>
                    <li onClick={(e) => {
                        e.preventDefault();
                        handleLogout();
                    }}>
                        <a><CiLogout className="logout-icon"/></a>
                    </li>
                </ul>
            </nav>
        </header>
    );
};

export default Header;