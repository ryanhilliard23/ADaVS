import React from 'react';
import '../css/global.css';

const Sidebar = () => {
  return (
    <nav className="sidebar-container">
      <div className="sidebar-header">
        <h2>ADaVS</h2>
      </div>
      <ul className="sidebar-nav">
        <li className="nav-item active">Dashboard</li>
        <li className="nav-item">Assets</li>
        <li className="nav-item">Vulnerabilities</li>
      </ul>
    </nav>
  );
};

export default Sidebar;