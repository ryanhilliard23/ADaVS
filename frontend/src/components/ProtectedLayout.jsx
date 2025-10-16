import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import '../css/global.css';

const ProtectedLayout = () => {
  const token = localStorage.getItem('accessToken');

  // If the user is not authenticated redirect them to the landing page
  if (!token) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <Outlet /> 
      </main>
    </div>
  );
};

export default ProtectedLayout;