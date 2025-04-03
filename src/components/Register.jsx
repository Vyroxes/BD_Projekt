import React, { useState, useEffect } from "react";
import { Eye, EyeOff } from "lucide-react";
import { FaUser, FaLock } from "react-icons/fa";
import { MdAlternateEmail } from "react-icons/md";
import { useNavigate } from "react-router-dom";
import { isAuthenticated, authAxios, setTokens } from '../utils/Auth';

import './Login.css';
import './Register.css';

const Register = ({ onLogin }) => {
    const [showPassword, setShowPassword] = useState(false);
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [password2, setPassword2] = useState("");
    const [dataError, setDataError] = useState("");
    const [loginError, setLoginError] = useState("");

    const navigate = useNavigate();

    useEffect(() => {
        const checkAuth = async () => {
            const result = await isAuthenticated();
            if (result) {
                navigate("/home");
            }
        };
        checkAuth();
    }, [navigate]);

    const isDisabled = dataError !== "" || username.trim() === "" || email.trim() === "" || password.trim() === "" || password2.trim() === "";

    const onSubmit = async () => {
        try {
            const response = await authAxios.post("/api/register", {
                username,
                email,
                password,
            });

            if (response.status === 201) {
                setTokens(
                    response.data.access_token,
                    response.data.refresh_token,
                    response.data.expire_time,
                    response.data.refresh_expire_time,
                    response.data.username,
                    response.data.email
                );
                onLogin();
                navigate('/home');
            }
        } catch (error) {
            console.error("Błąd podczas rejestrowania: ", error);

            if (error.response && error.response.data && error.response.data.message) {
                setLoginError(error.response.data.message);
            } else {
                setLoginError("Błąd podczas rejestrowania.");
            }
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (dataError) return;

        setLoginError('');

        await onSubmit();
    };

    return (
        <div className="container-login">
            <div className="container-login2">
                <h1>Rejestrowanie</h1>
                <form onSubmit={handleSubmit}>
                    <div className="login-group">
                        <FaUser className="login-icons" />
                        <input
                            type="text"
                            id="username"
                            name="username"
                            required
                            minLength="5"
                            maxLength="20"
                            placeholder="Nazwa użytkownika"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                        />
                    </div>
                    <div className="login-group">
                        <MdAlternateEmail className="login-icons" />
                        <input
                            type="email"
                            id="email"
                            name="email"
                            required
                            minLength="6"
                            maxLength="320"
                            placeholder="Email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </div>
                    <div className="login-group">
                        <FaLock className="login-icons" />
                        <input
                            type={showPassword ? "text" : "password"}
                            id="password"
                            name="password"
                            required
                            minLength="8"
                            maxLength="20"
                            placeholder="Hasło"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                        <div>
                            <button
                                className="register-button-show-password"
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                            >
                                {showPassword ? <Eye size={20} /> : <EyeOff size={20} />}
                            </button>
                        </div>
                    </div>
                    <div className="login-group">
                        <FaLock className="login-icons" />
                        <input
                            type={showPassword ? "text" : "password"}
                            id="password2"
                            name="password2"
                            required
                            minLength="8"
                            maxLength="20"
                            placeholder="Powtórz hasło"
                            value={password2}
                            onChange={(e) => setPassword2(e.target.value)}
                        />
                    </div>
                    {dataError && <div className="register-error-text">
                        <label>{dataError}</label>
                    </div>}
                    {loginError && <div className="register-error-text2">
                        <label>{loginError}</label>
                    </div>}
                    <div className="login-controls">
                        <button type="submit" disabled={isDisabled}>
                            Zarejestruj się
                        </button>
                    </div>
                    <div className="login-register">
                        <label>Masz konto?</label>
                        <button type="button" onClick={() => navigate("/login")}>
                            Zaloguj się
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default Register;