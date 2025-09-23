import React from 'react';
import { NavLink } from 'react-router-dom'; 
import '../css/global.css';

const Sidebar = () => {
  return (
    <nav className="sidebar-container">
      <div className="sidebar-header">
        <h2>ADaVS</h2>
      </div>
      <ul className="sidebar-nav">
        <NavLink to="/" className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}>
          Dashboard
        </NavLink>
        <NavLink to="/assets" className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}>
          Assets
        </NavLink>
        <NavLink to="/vulnerabilities" className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}>
          Vulnerabilities
        </NavLink>
      </ul>
    </nav>
  );
};

export default Sidebar;