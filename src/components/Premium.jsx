import React from 'react';
import { useNavigate } from "react-router-dom";
import { isAuthenticated } from '../utils/Auth';

import './Premium.css';

const Premium = () => {
    const navigate = useNavigate();

    return (
        <div className='container'>
            <label>Premium</label>
        </div>
    );
};

export default Premium;