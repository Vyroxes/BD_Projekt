import { CiLogout } from "react-icons/ci";
import { useNavigate } from "react-router-dom";
import { isAuthenticated, getCookie, clearTokens, authAxios } from '../utils/Auth';

import './Header.css';

const Header = () => {
    const username = isAuthenticated() ? getCookie("username") : "";
    const navigate = useNavigate();

    const handleLogout = async () => {
        try {
            const response = await authAxios.post("/api/logout", {
                refresh_token: getCookie("refresh_token")
            });
            
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
                    {isAuthenticated() && (
                        <li onClick={(e) => {
                            e.preventDefault();
                            handleLogout();
                        }}>
                            <a>{username}&nbsp;<CiLogout className="logout-icon"/></a>
                        </li>
                    )}
                </ul>
            </nav>
        </header>
    );
};

export default Header;