import React from 'react';
import { NavLink } from 'react-router-dom';
import { MdDashboard, MdStorage, MdSecurity, MdLogout, MdOutlineMenuOpen } from 'react-icons/md';
import { FaGithub, FaUserCircle } from 'react-icons/fa';
import { FiSun, FiMoon } from 'react-icons/fi';
import '/src/css/Sidebar.css';
import adavsLogo from '/src/assets/adavs.png';

const Sidebar = ({ isCollapsed, toggleSidebar, onLogout, userEmail, theme, toggleTheme }) => {
  
  return (
    <nav className={`sidebar-container ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <img src={adavsLogo} alt="ADaVS Logo" className="header-logo" />
        <h2 className="sidebar-title">ADaVS</h2>
        <button onClick={toggleSidebar} className="header-toggle-button" aria-label="Close Sidebar">
          <MdOutlineMenuOpen />
        </button>
      </div>

      <div className="sidebar-profile">
        <FaUserCircle className="profile-icon" />
        <span className="profile-email" title={userEmail}>
          {userEmail || "..."}
        </span>
        <button onClick={onLogout} className="profile-logout-button" aria-label="Sign Out">
          <MdLogout />
        </button>
      </div>

      {/* Navigation Links */}
      <ul className="sidebar-nav">
        <li>
          <NavLink to="/dashboard" className={({ isActive }) => "nav-item" + (isActive ? " active" : "")} end>
            <MdDashboard className="nav-icon" />
            <span className="nav-text">Dashboard</span>
          </NavLink>
        </li>
        <li>
          <NavLink to="/assets" className={({ isActive }) => "nav-item" + (isActive ? " active" : "")}>
            <MdStorage className="nav-icon" />
            <span className="nav-text">Assets</span>
          </NavLink>
        </li>
        <li>
          <NavLink to="/vulnerabilities" className={({ isActive }) => "nav-item" + (isActive ? " active" : "")}>
            <MdSecurity className="nav-icon" />
            <span className="nav-text">Vulnerabilities</span>
          </NavLink>
        </li>
      </ul>

      {/* Footer */}
      <div className="sidebar-footer">
         <a href="https://github.com/ryanhilliard23/ADaVS" target="_blank" rel="noopener noreferrer" className="footer-icon-button github-icon-button">
             <FaGithub className="nav-icon" />
         </a>
         <button onClick={toggleTheme} className="footer-icon-button" aria-label="Toggle theme">
           {theme === 'dark' ? <FiSun /> : <FiMoon />}
         </button>
      </div>
    </nav>
  );
};

export default Sidebar;