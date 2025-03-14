import React, { useState } from "react";
import { CiLogout } from "react-icons/ci";
import useSignOut from 'react-auth-kit/hooks/useSignOut';
import useIsAuthenticated from 'react-auth-kit/hooks/useIsAuthenticated'
import useAuthUser from 'react-auth-kit/hooks/useAuthUser'

import './Header.css';

const Header = () => {
    const isAuthenticated = useIsAuthenticated();
    const signOut = useSignOut();
    const authUser = useAuthUser();
    let username = "";

    if(isAuthenticated)
    {
        username = authUser.name;
    }
    
    const handleLogout = () => {
        signOut();
    }

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
                    <li onClick={handleLogout}>
                        <a href="/login">{username}&nbsp;<CiLogout className="logout-icon"/></a>
                    </li>
                </ul>
            </nav>
        </header>
    );
};

export default Header;