import React, { useState } from 'react';
import { useNavigate } from "react-router-dom";
import { authAxios } from '../utils/Auth';

import './Contact.css';

const Contact = () => {
    const navigate = useNavigate();

    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [subject, setSubject] = useState("");
    const [text, setText] = useState("");

    const onSubmit = async () => {
        try {
            const response = await authAxios.post("/api/contact", {
                username,
                email,
                subject,
                text,
            });

            if (response.status === 201) {
                console.log("Message sent successfully.");
            }
        } catch (error) {
            console.error("Error sending message:", error);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        await onSubmit();
    };

    return (
        <div className='contact-container'>
            <h1>Kontakt</h1>
            <div className='contact-container2'>
                <form onSubmit={handleSubmit}>
                    <div className='contact-row'>
                        <label>
                            Nazwa użytkownika
                            <input
                                type="text"
                                id="username"
                                name='username'
                                required
                                value={username}
                                minLength="5"
                                maxLength="20"
                                onChange={(e) => setUsername(e.target.value)}
                            />
                        </label>
                    </div>
                    <div className='contact-row'>
                        <label>
                            Email
                            <input
                                type="email"
                                id="email"
                                name='email'
                                required
                                value={email}
                                minLength="6"
                                maxLength="320"
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </label>
                    </div>
                    <div className='contact-row'>
                        <label>
                            Temat
                            <input
                                type="text"
                                id="subject"
                                name='subject'
                                required
                                value={subject}
                                minLength="1"
                                maxLength="50"
                                onChange={(e) => setSubject(e.target.value)}
                            />
                        </label>
                    </div>
                    <div className='contact-row'>
                        <label>Wiadomość
                            <textarea
                                id="text"
                                name='text'
                                value={text}
                                required
                                minLength="1"
                                maxLength="500"
                                onChange={(e) => setText(e.target.value)}
                            />
                        </label>
                    </div>
                    <div className='contact-button'>
                        <button type="submit">Wyślij wiadomość</button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default Contact;