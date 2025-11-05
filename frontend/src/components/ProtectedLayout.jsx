import React, { useState, useEffect, useRef } from 'react';
import { Navigate, Outlet, useLocation, useOutletContext } from 'react-router-dom';
import Sidebar from './Sidebar.jsx';
import '../css/ProtectedLayout.css';
import { MdOutlineMenu, MdLogout } from 'react-icons/md';
import { FaUserCircle } from 'react-icons/fa';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const ProtectedLayout = ({ theme, toggleTheme }) => {
  const token = localStorage.getItem('accessToken');
  
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false); 
  
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [userEmail, setUserEmail] = useState("");
  
  // Refs for closing popover when clicking outside
  const userMenuRef = useRef(null);
  const avatarButtonRef = useRef(null);
  const location = useLocation();

  // Effect to fetch user data once
  useEffect(() => {
    const fetchUserData = async () => {
      const token = localStorage.getItem('accessToken');
      if (!token) return;
      try {
        const response = await fetch(`https://adavs-backend.onrender.com/api/users/me`, {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (response.ok) {
          const data = await response.json();
          setUserEmail(data.email);
        } else {
          console.error("Failed to fetch user data. Token might be invalid");
        }
      } catch (error) {
        console.error("Error fetching user data:", error);
      }
    };
    fetchUserData();
  }, []);

  // Effect to handle clicking outside the user menu
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        userMenuRef.current && 
        !userMenuRef.current.contains(event.target) &&
        avatarButtonRef.current &&
        !avatarButtonRef.current.contains(event.target)
      ) {
        setIsUserMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  if (!token) {
    return <Navigate to="/" replace />;
  }

  const toggleSidebar = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
    setIsUserMenuOpen(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    window.location.href = '/';
  };

  return (
    <div className="protected-layout-container">
      <Sidebar 
        isCollapsed={isSidebarCollapsed} 
        toggleSidebar={toggleSidebar} 
        onLogout={handleLogout} 
        userEmail={userEmail}
        theme={theme}
        toggleTheme={toggleTheme} 
      />
      <div className="top-bar-controls">
        <div className="top-left-controls">
                    
          {isSidebarCollapsed && (
            <button onClick={toggleSidebar} className="floating-toggle-button" ria-label="Open Sidebar">
              <MdOutlineMenu />
            </button>
          )}
          
          {isSidebarCollapsed && (
            <div className="user-menu-container">
              <button ref={avatarButtonRef} onClick={() => setIsUserMenuOpen(prev => !prev)} className="avatar-button" aria-label="User Menu">
                <FaUserCircle />
              </button>

              {isUserMenuOpen && (
                <div ref={userMenuRef} className="user-menu-popover">
                  <div className="user-email">{userEmail}</div>
                  <button className="logout-button" onClick={handleLogout}>
                    <MdLogout />
                    <span>Sign Out</span>
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <main className={`main-content-area ${isSidebarCollapsed ? 'sidebar-collapsed' : 'sidebar-expanded'}`}>
        <Outlet context={{ userEmail }} />
      </main>
    </div>
  );
};

export default ProtectedLayout;