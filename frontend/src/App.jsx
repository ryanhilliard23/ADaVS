// STEP 1: Import useEffect
import React, { useEffect } from 'react'; 
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

  return (
    <>
      <Particles
        particleColors={['#ffffff', '#ffffff']}
        particleCount={200} 
        particleSpread={10}
        speed={0.05} 
        particleBaseSize={50}
        moveParticlesOnHover={isLandingPage}  
        alphaParticles={true}
        disableRotation={false}
      />

      <Routes>
        <Route element={<RedirectIfLoggedIn />}>
          <Route path="/" element={<LandingPage />} />
        </Route>

        <Route element={<ProtectedLayout />}>
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