import React from 'react';
import { NavLink } from 'react-router-dom';
import { MdDashboard, MdStorage, MdSecurity } from 'react-icons/md';
import '../css/global.css';
import adavsLogo from '../assets/adavs.png';

const Sidebar = () => {
  return (
    <nav className="sidebar-container">
      <div className="sidebar-header">
        <img src={adavsLogo} alt="ADaVS Logo" className="header-logo" />
        <h2>ADaVS</h2>
      </div>

      <div className="nav-links-container">
        <ul className="sidebar-nav">
          <NavLink to="/" className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}>
            <MdDashboard className="nav-icon" />
            Dashboard
          </NavLink>
          <NavLink to="/assets" className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}>
            <MdStorage className="nav-icon" />
            Assets
          </NavLink>
          <NavLink to="/vulnerabilities" className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}>
            <MdSecurity className="nav-icon" />
            Vulnerabilities
          </NavLink>
          <NavLink to="/scans" className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}>
            <MdSecurity className="nav-icon" />
            Scans
          </NavLink>
        </ul>
      </div>
    </nav>
  );
};

export default Sidebar;