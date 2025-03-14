import React, { useEffect } from 'react';
import useIsAuthenticated from 'react-auth-kit/hooks/useIsAuthenticated'
import { useNavigate } from "react-router-dom";

const Home = () =>
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
            <label>Strona główna</label>
        </div>
    );
};

export default Home;