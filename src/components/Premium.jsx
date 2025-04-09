import React from 'react';
import { useNavigate } from "react-router-dom";
import { MdHighlightOff } from "react-icons/md";
import { IoBookOutline } from "react-icons/io5";
import { RxAvatar } from "react-icons/rx";
import { HiCollection } from "react-icons/hi";
import { AiFillStar } from "react-icons/ai";
import { MdOutlineDarkMode } from "react-icons/md";
import { IoIosStats } from "react-icons/io";
import { AiFillMail } from "react-icons/ai";

import './Premium.css';

const Premium = () => {
    const navigate = useNavigate();

    return (
        <div className='premium-container'>
            <h1>Premium</h1>
            <div className='premium-cards'>
                <div className='premium-content'>
                    <h2>PREMIUM</h2>
                    <h3>19,99 zł</h3>
                    <a><MdHighlightOff className='icons'/>Brak reklam</a>
                    <a><IoBookOutline className='icons'/>Import i eksport książek</a>
                    <a><RxAvatar className='icons'/>Animowany awatar</a>
                    <a><HiCollection className='icons'/>Większy limit książek</a>
                    <div className='premium-button'>
                        <button>Kup pakiet PREMIUM</button>
                    </div>    
                </div>
                <div className='premiumplus-content'>
                    <h2>PREMIUM+</h2>
                    <h3>34,99 zł</h3>
                    <a><AiFillStar className='icons'/>Wszystko co pakiet PREMIUM</a>
                    <a><MdOutlineDarkMode className='icons'/>Motywy kolorystyczne</a>
                    <a><IoIosStats className='icons'/>Zaawansowane statystyki</a>
                    <a><AiFillMail className='icons'/>Powiadomienia o nowych książkach</a>
                    <div className='premiumplus-button'>
                        <button>Kup pakiet PREMIUM+</button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Premium;