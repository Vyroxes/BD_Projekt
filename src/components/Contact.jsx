import React, { useEffect } from 'react';
import useIsAuthenticated from 'react-auth-kit/hooks/useIsAuthenticated'
import { useNavigate } from "react-router-dom";

import './Contact.css';

const Contact = () =>
{
    const isAuthenticated = useIsAuthenticated();
    const navigate = useNavigate();

    useEffect(() => 
    {
        if (!isAuthenticated) 
        {
            navigate('/login');
        }
    }, [isAuthenticated, navigate]);

    return (
        <div className='container'>
            <label>Kontakt</label>
        </div>
    );
};

export default Contact;