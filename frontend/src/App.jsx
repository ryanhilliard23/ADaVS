import React, { useEffect, useState } from 'react'; 
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import ProtectedLayout from './components/ProtectedLayout';
import RedirectIfLoggedIn from './components/RedirectIfLoggedIn';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import Assets from './pages/Assets';
import Vulnerabilities from './pages/Vulnerabilities';
import Particles from './components/Particles';
import './css/global.css'; 

function App() {
  const location = useLocation(); 
  const isLandingPage = location.pathname === '/';

  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark');

  const toggleTheme = () => {
    setTheme((prevTheme) => {
      const newTheme = prevTheme === 'dark' ? 'light' : 'dark';
      localStorage.setItem('theme', newTheme);
      return newTheme;
    });
  };

  useEffect(() => {
    document.body.className = theme;
  }, [theme]);

  useEffect(() => {
    const baseTitle = 'ADaVS';
    let pageTitle = 'Home';

    switch (location.pathname) {
      case '/':
        pageTitle = 'Home';
        break;
      case '/dashboard':
        pageTitle = 'Dashboard';
        break;
      case '/assets':
        pageTitle = 'Assets';
        break;
      case '/vulnerabilities':
        pageTitle = 'Vulnerabilities';
        break;
      default:
        pageTitle = 'Page Not Found';
    }
    
    document.title = `${baseTitle} | ${pageTitle}`;

  }, [location]);

  const particleColors = theme === 'dark' ? ['#ffffff', '#ffffff'] : ['#000000', '#000000'];

  return (
    <>
      <Particles
        particleColors={particleColors}
        particleCount={500} 
        particleSpread={10}
        speed={0.5} 
        particleBaseSize={3}
        moveParticlesOnHover={isLandingPage}  
        alphaParticles={true}
        disableRotation={true}
        sizeRandomness={0}
      />

      <Routes>
        <Route element={<RedirectIfLoggedIn />}>
          <Route path="/" element={<LandingPage theme={theme} toggleTheme={toggleTheme} />} />
        </Route>

        <Route element={<ProtectedLayout theme={theme} toggleTheme={toggleTheme} />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/assets" element={<Assets />} />
          <Route path="/vulnerabilities" element={<Vulnerabilities />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}

export default App;