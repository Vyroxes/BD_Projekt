import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import createStore from 'react-auth-kit/createStore';
import AuthProvider from 'react-auth-kit';
import './App.css';

const Login = lazy(() => import('./components/Login'));
const Register = lazy(() => import('./components/Register'));
const Home = lazy(() => import('./components/Home'));
const BookCollection = lazy(() => import('./components/BookCollection'));
const WishList = lazy(() => import('./components/WishList'));
const Premium = lazy(() => import('./components/Premium'));
const Contact = lazy(() => import('./components/Contact'));
const Header = lazy(() => import('./components/Header'));
const Footer = lazy(() => import('./components/Footer'));

const store = createStore({
  authName:'access_token',
  authType:'cookie',
  cookieDomain: window.location.hostname,
  cookieSecure: true,
});

const App = () =>
{
  const location = useLocation();

  return (
    <AuthProvider store={store}>
      {location.pathname !== '/login' && location.pathname !== '/register' && (<Suspense><Header/></Suspense>)}
      <Routes>
        <Route path="/login" element={<Suspense><Login/></Suspense>}/>
        <Route path="/register" element={<Suspense><Register/></Suspense>}/>
        <Route path="/home" element={<Suspense><Home/></Suspense>}/>
        <Route path="/book-collection" element={<Suspense><BookCollection/></Suspense>}/>
        <Route path="/wish-list" element={<Suspense><WishList/></Suspense>}/>
        <Route path="/contact" element={<Suspense><Contact/></Suspense>}/>
        <Route path="/premium" element={<Suspense><Premium/></Suspense>}/>
        <Route path="*" element={<Navigate to="/home"/>}/>
      </Routes>
      {location.pathname !== '/login' && location.pathname !== '/register' && (<Suspense><Footer/></Suspense>)}
    </AuthProvider>
  );
}

export default App;