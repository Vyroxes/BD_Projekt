import React, { useState, useEffect} from "react";
import useSignIn from 'react-auth-kit/hooks/useSignIn';
import { Eye, EyeOff } from "lucide-react";
import { FaUser, FaLock } from "react-icons/fa";
import { MdAlternateEmail } from "react-icons/md";
import useIsAuthenticated from 'react-auth-kit/hooks/useIsAuthenticated'
import { useNavigate } from "react-router-dom";
import axios from "axios";

import './Login.css';
import './Register.css';

const Register = () => {
    const [showPassword, setShowPassword] = useState(false);
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [password2, setPassword2] = useState("");
    const [dataError, setDataError] = useState("");
    const [loginError, setLoginError] = useState("");

    const signIn = useSignIn();
    const navigate = useNavigate();
    const isAuthenticated = useIsAuthenticated();

    const isDisabled = dataError !== "" || username.trim() === "" || email.trim() === ""  || password.trim() === "" || password2.trim() === "";
    const isDisabled2 = password.trim() === "";
    const isDisabled3 = password.trim() === "" || (dataError !== '' && dataError !== "Hasła muszą być jednakowe." && dataError !== "Nazwa użytkownika nie może zawierać spacji." && dataError !== "Email nie może zawierać spacji." && dataError !== "Hasło nie może zawierać spacji.")

    const spacebar = /\s/;
    const number = /\d/;
    const specialchar = /[!@#$%^&*(),.?":{}|<>]/;

    useEffect(() => 
    {
        if (isAuthenticated) 
        {
            navigate('/home');
        }
    }, [isAuthenticated, navigate]);

    const onSubmit = async () => {
        try {
            const response = await axios.post("http://localhost:5000/register", {
                username,
                email,
                password,
            }, {
                withCredentials: true
            });

            if (response.status == 201)
            {
                console.log(response.data.message);
                if(signIn({
                    auth: {
                        token: response.data.access_token,
                        type: 'Bearer'
                    },
                    userState: {
                        name: response.data.username,
                    }
                }))
                {
                    navigate('/home');
                }
            }
        } catch (error) {
            console.error("Błąd podczas rejestrowania: ", error);

            if (error.response && error.response.data && error.response.data.message) {
                setLoginError(error.response.data.message);
            }
            else
            {
                setLoginError("Błąd podczas rejestrowania.");
            }
        }
    };

    const checkUsername = (value) => {
        if (spacebar.test(value)) {
            setDataError("Nazwa użytkownika nie może zawierać spacji.");
            value = value.replace(/\s/g, "");

            setTimeout(() => {
                setDataError("");
            }, 2000);
        }

        setUsername(value);
    };

    const checkEmail = (value) => {
        if (spacebar.test(value)) {
            setDataError("Email nie może zawierać spacji.");
            value = value.replace(/\s/g, "");

            setTimeout(() => {
                setDataError("");
            }, 2000);
        }

        setEmail(value);
    };

    const checkPassword = (value) => {
        if (spacebar.test(value)) {
            setDataError("Hasło nie może zawierać spacji.");
            value = value.replace(/\s/g, "");

            setTimeout(() => {
                setDataError("");
            }, 2000);
        } else if (value.length < 8 || value.length > 20) {
            setDataError("Hasło musi zawierać od 8 do 20 znaków.");
        } else if (!number.test(value)) {
            setDataError("Hasło musi zawierać co najmniej jedną cyfrę.");
        } else if (!specialchar.test(value)) {
            setDataError('Hasło musi zawierać co najmniej jeden znak specjalny [!@#$%^&*(),.?":{}|<>].');
        } else {
            setDataError('');
        }

        setPassword(value);
    };

    const checkPassword2 = (value) => {
        if (spacebar.test(value)) {
            setDataError("Hasło nie może zawierać spacji.");
            value = value.replace(/\s/g, "");
        }
        else if (value !== password) {
            setDataError("Hasła muszą być jednakowe.");
        }
        else
        {
            setDataError("");
        }

        setPassword2(value);
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
                        <FaUser className="login-icons"/>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            required
                            minLength="5"
                            maxLength="20"
                            placeholder="Nazwa użytkownika"
                            value={username}
                            onChange={(e) => { checkUsername(e.target.value) }}
                        />
                    </div>
                    <div className="login-group">
                        <MdAlternateEmail className="login-icons"/>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            required
                            minLength="6"
                            maxLength="320"
                            placeholder="Email"
                            value={email}
                            onChange={(e) => { checkEmail(e.target.value) }}
                        />
                    </div>
                    <div className="login-group">
                        <FaLock className="login-icons"/>
                        <input
                            type={showPassword ? "text" : "password"}
                            id="password"
                            name="password"
                            required
                            minLength="8"
                            maxLength="20"
                            placeholder="Hasło"
                            value={password}
                            onChange={(e) => { checkPassword(e.target.value) }}
                        />
                        <div>
                            <button
                                className="register-button-show-password"
                                type="button"
                                disabled={isDisabled2}
                                onClick={() => setShowPassword(!showPassword)}
                            >
                                {showPassword ? <Eye size={20} /> : <EyeOff size={20} />}
                            </button>
                        </div>
                    </div>
                    <div className="login-group">
                        <FaLock className="login-icons"/>
                        <input
                            type={showPassword ? "text" : "password"}
                            id="password2"
                            name="password2"
                            required
                            minLength="8"
                            maxLength="20"
                            placeholder="Powtórz hasło"
                            value={password2}
                            disabled={isDisabled3}
                            onChange={(e) => { checkPassword2(e.target.value) }}
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