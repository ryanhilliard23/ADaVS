import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaGithub } from 'react-icons/fa';
import { MdSpaceDashboard } from 'react-icons/md';
import Login from '../components/Login';
import Register from '../components/Register';
import adavsLogo from '../assets/adavs.png';
import '../css/landing.css'; 

const LandingPage = () => {
  const [mode, setMode] = useState('login'); 
  const navigate = useNavigate();

  const handleSwitchMode = (newMode) => {
    setMode(newMode);
  };

  return (
    <div className="landing-container">
      <div className="landing-info-panel">
        <div className="info-content">
          <img src={adavsLogo} alt="ADaVS Logo" className="landing-logo" />

          <h1>ADaVS</h1>
          <p>Asset Discovery and Vulnerability Scanner</p>
          <div className="button-group">
            <a href="https://github.com/ryanhilliard23/ADaVS" target="_blank" rel="noopener noreferrer" className="github-button">
              <FaGithub />
              Go to GitHub
            </a>
          </div>
        </div>
      </div>

      <div className="landing-auth-panel">
        {mode === 'login' ? (
          <Login onSwitchMode={handleSwitchMode} />
        ) : (
          <Register onSwitchMode={handleSwitchMode} />
        )}
      </div>
    </div>
  );
};

export default LandingPage;