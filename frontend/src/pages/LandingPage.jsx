import React, { useState } from 'react';
import { FaGithub } from 'react-icons/fa';
import { MdLogin } from 'react-icons/md';
import Login from '../components/Login';
import Register from '../components/Register';
import adavsLogo from '../assets/adavs.png';
import '../css/landing.css'; 

const LandingPage = () => {
  const [modalMode, setModalMode] = useState(null);

  const openModal = (mode) => {
    setModalMode(mode);
  };

  const closeModal = () => {
    setModalMode(null);
  };

  const switchModalMode = (newMode) => {
    setModalMode(newMode);
  }

  return (
    <div className="landing-container-fullscreen">  

      <div className="landing-content-center">
        <img src={adavsLogo} alt="ADaVS Logo" className="landing-logo-center" />
        <h1>ADaVS</h1>
        <p>Asset Discovery and Vulnerability Scanner</p>
        <div className="landing-button-group-center">
          <button onClick={() => openModal('login')} className="landing-action-button">
            <MdLogin />
            <span>Sign In</span>
          </button>
        </div>
      </div>

      <div className="landing-bottom-bar">
        <a href="https://github.com/ryanhilliard23/ADaVS" target="_blank" rel="noopener noreferrer" className="github-button-bottom">
          <FaGithub />
          GitHub
        </a>
      </div>

      {modalMode && (
        <div className="modal-backdrop" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close-button" onClick={closeModal}>&times;</button>
            {modalMode === 'login' ? (
              <Login onSwitchMode={switchModalMode} />
            ) : (
              <Register onSwitchMode={switchModalMode} />
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default LandingPage;