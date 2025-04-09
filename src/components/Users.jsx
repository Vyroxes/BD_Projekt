import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { IoMdClose } from "react-icons/io";
import { authAxios, getCookie } from '../utils/Auth';

import './Users.css';

const Users = () => {
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");
    const [users, setUsers] = useState([]);
    
    const currentUsername = getCookie("username");
    const adminUsername = import.meta.env.VITE_ADMIN_USERNAME;
    const navigate = useNavigate();

    const isDisabled = search.trim() === "";

    useEffect(() => {
        fetchUsers();
    }, []);

    const fetchUsers = async () => {
        try {
            const response = await authAxios.get("/api/users");
            if (response.status === 200) {
                const filteredUsers = response.data.filter(user => user.username !== currentUsername);
                setUsers(filteredUsers);
                setLoading(false);
            }
        }
        catch (error) {
            console.error("Błąd podczas pobierania danych użytkowników: ", error);
        }
    };

    const filteredUsers = users.filter((user) =>
        user.username.toLowerCase().includes(search.toLowerCase())
    );

    if(loading) {
        return;
    }

    return (
        <div className="users-container">
            <div className="users-search-bar">
                <input
                    type="text"
                    id="search"
                    name="search"
                    placeholder="Szukaj użytkownika"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                />
                <button
                    className="users-clear-search"
                    type="button"
                    disabled={isDisabled}
                    onClick={() => setSearch("")}
                >
                    <IoMdClose />
                </button>
            </div>
            <ul className="users-list">
                {filteredUsers.length === 0 && (
                    <a className='no-users-found '>Brak innych użytkowników</a>
                )}
                {filteredUsers.map((user, index) => (
                    <li
                        key={user.username}
                        className="user-item"
                        style={{ '--index': index }}
                        onClick={() => navigate(`/users/${user.username}`)}
                    >
                        <img
                            src={user.avatar_url || "/unknown_avatar.jpg"}
                            alt={user.username}
                            className="users-avatar"
                            onError={(e) => {
                                e.target.onerror = null;
                                e.target.src = "/unknown_avatar.jpg";
                            }}
                            loading="lazy"
                        />
                        <div className="user-item-info">
                            <span className="user-item-name">{user.username}</span>
                            <span className="user-item-email">{user.email}</span>
                        </div>
                        {user.username === adminUsername && (
                            <span className="user-item-role user-item-admin">Admin</span>
                        )}
                        {user.username !== adminUsername && (
                            <span className="user-item-role">Użytkownik</span>
                        )}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Users;