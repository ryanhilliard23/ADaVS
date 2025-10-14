import React from 'react';
import { NavLink } from 'react-router-dom';
import { MdHome, MdDashboard, MdStorage, MdSecurity } from 'react-icons/md';
import '../css/global.css';
import adavsLogo from '../assets/adavs.png';

const Sidebar = () => {
  return (
    <nav className="sidebar-container">
      <div className="sidebar-header">
        <img src={adavsLogo} alt="ADaVS Logo" className="header-logo" />
        <h2>ADaVS</h2>
      </div>

      <div className="nav-area">
        <NavLink to="/" className={({ isActive }) => "nav-item home-button" + (isActive ? " active" : "")}>
          <MdHome className="nav-icon" />
        </NavLink>

        <div className="nav-links-container">
          <ul className="sidebar-nav">
            <NavLink to="/dashboard" className={({ isActive }) => "nav-item" + (isActive ? " active" : "")}>
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
      </div>
    </nav>
  );
};

export default Sidebar;