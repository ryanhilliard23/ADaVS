import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedLayout from './components/ProtectedLayout';
import RedirectIfLoggedIn from './components/RedirectIfLoggedIn';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import Assets from './pages/Assets';
import Vulnerabilities from './pages/Vulnerabilities';
import './css/global.css'; 

function App() {
  return (
    <Routes>
      {/* Redirects if you are already logged in */}
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
  );
}

export default App;