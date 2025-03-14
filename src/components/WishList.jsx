import React, { useEffect } from 'react';
import useIsAuthenticated from 'react-auth-kit/hooks/useIsAuthenticated'
import { useNavigate } from "react-router-dom";

import './WishList.css';

const WishList = () =>
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
            <label>Lista życzeń</label>
        </div>
    );
};

export default WishList;