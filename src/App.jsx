import React, { Suspense, lazy, useState, useEffect } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { isAuthenticated } from './utils/Auth';

import './App.css';

const Login = lazy(() => import('./components/Login'));
const Register = lazy(() => import('./components/Register'));
const Home = lazy(() => import('./components/Home'));
const Books = lazy(() => import('./components/Books'));
const BookDetails = lazy(() => import('./components/BookDetails'));
const AddBook = lazy(() => import('./components/AddBook'));
const EditBook = lazy(() => import('./components/EditBook'));
const ReviewBook = lazy(() => import('./components/ReviewBook'));
const Premium = lazy(() => import('./components/Premium'));
const Contact = lazy(() => import('./components/Contact'));
const Header = lazy(() => import('./components/Header'));
const Footer = lazy(() => import('./components/Footer'));

const App = () => {
  const location = useLocation();

  const [authState, setAuthState] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      const result = await isAuthenticated();
      setAuthState(result);
    };

    checkAuth();
  }, [location]);

  if (authState === null) {
    return null;
  }

  return (
    <Suspense>
      <div className='app'>
        {location.pathname !== '/login' && location.pathname !== '/register' && (<Header />)}
        <Routes>
          <Route path="/login" element={<Login onLogin={() => setAuthState(true)}/>} />
          <Route path="/register" element={<Register onLogin={() => setAuthState(true)}/>} />
          <Route path="/home" element={authState ? <Home /> : <Navigate to="/login" />} />
          <Route path="/book-collection" element={authState ? <Books /> : <Navigate to="/login" />} />
          <Route path="/wish-list" element={authState ? <Books /> : <Navigate to="/login" />} />
          <Route path="/bc-book-details/:id" element={authState ? <BookDetails /> : <Navigate to="/login" />} />
          <Route path="/wl-book-details/:id" element={authState ? <BookDetails /> : <Navigate to="/login" />} />
          <Route path="/bc-add-book" element={authState ? <AddBook /> : <Navigate to="/login" />} />
          <Route path="/wl-add-book" element={authState ? <AddBook /> : <Navigate to="/login" />} />
          <Route path="/bc-edit-book/:id" element={authState ? <EditBook /> : <Navigate to="/login" />} />
          <Route path="/wl-edit-book/:id" element={authState ? <EditBook /> : <Navigate to="/login" />} />
          <Route path="/bc-review-book/:id" element={authState ? <ReviewBook /> : <Navigate to="/login" />} />
          <Route path="/wl-review-book/:id" element={authState ? <ReviewBook /> : <Navigate to="/login" />} />
          <Route path="/contact" element={authState ? <Contact /> : <Navigate to="/login" />} />
          <Route path="/premium" element={authState ? <Premium /> : <Navigate to="/login" />} />
          <Route path="*" element={<Navigate to="/home" />} />
        </Routes>
        {location.pathname !== '/login' && location.pathname !== '/register' && (<Footer />)}
      </div>
    </Suspense>
  );
};

export default App;