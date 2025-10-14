import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import '../css/global.css';

const AppLayout = () => {
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        {/* Child routes (Dashboard, Assets, Vulnerabilities)*/}
        <Outlet /> 
      </main>
    </div>
  );
};

export default AppLayout;