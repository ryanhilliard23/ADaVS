import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';

const RedirectIfLoggedIn = () => {
  const token = localStorage.getItem('accessToken');

  // If a token exists, the user is logged in redirect them to the dashboard
  if (token) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
};

export default RedirectIfLoggedIn;