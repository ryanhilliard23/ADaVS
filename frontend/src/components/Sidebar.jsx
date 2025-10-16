import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { MdDashboard, MdStorage, MdSecurity, MdLogout } from 'react-icons/md';
import '../css/global.css';
import adavsLogo from '../assets/adavs.png';

const Sidebar = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    navigate('/');
  };

  return (
    <nav className="sidebar-container">
      <div className="sidebar-header">
        <img src={adavsLogo} alt="ADaVS Logo" className="header-logo" />
        <h2>ADaVS</h2>
      </div>

      <div className="nav-area">
        <div className="nav-links-container">
          <ul className="sidebar-nav">
            <NavLink to="/dashboard" className={({ isActive }) => "nav-item" + (isActive ? " active" : "")} end>
              <MdDashboard className="nav-icon" />
              Dashboard
            </NavLink>
            <NavLink to="/assets" className={({ isActive }) => "nav-item" + (isActive ? " active" : "")}>
              <MdStorage className="nav-icon" />
              Assets
            </NavLink>
            <NavLink to="/vulnerabilities" className={({ isActive }) => "nav-item" + (isActive ? " active" : "")}>
              <MdSecurity className="nav-icon" />
              Vulnerabilities
            </NavLink>
          </ul>
        </div>

        <button onClick={handleLogout} className="nav-item logout-button">
          <MdLogout className="nav-icon" />
          Logout
        </button>
      </div>
    </nav>
  );
};

export default Sidebar;