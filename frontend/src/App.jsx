import { Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './components/AppLayout';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import Assets from './pages/Assets';
import Vulnerabilities from './pages/Vulnerabilities';
import './css/global.css'; 

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />

      <Route element={<AppLayout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/assets" element={<Assets />} />
        <Route path="/vulnerabilities" element={<Vulnerabilities />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;