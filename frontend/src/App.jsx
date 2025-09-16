import { useState } from "react";
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Assets from './pages/Assets';
import Vulnerabilities from './pages/Vulnerabilities';
import './css/global.css'; 

function App() {
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <Dashboard />
        <Assets />
        <Vulnerabilities />
      </main>
    </div>
  );
}

export default App;
