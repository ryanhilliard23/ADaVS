import React, { useState, useEffect } from "react";
import { FaBullseye } from 'react-icons/fa';
import "../css/dashboard.css"; 

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const Dashboard = () => {
  const [targets, setTarget] = useState("");
  const [isScanning, setIsScanning] = useState(false);
  const [scanMessage, setScanMessage] = useState("");
  const [userEmail, setUserEmail] = useState(""); 

  useEffect(() => {
    const fetchUserData = async () => {
      const token = localStorage.getItem('accessToken');
      if (!token) {
        return;
      }

      try {
        const response = await fetch(`${API_BASE_URL}/users/me`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
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
  }, []); // empty array ensures runs only on component mount

  const handleStartScan = async () => {
    if (!targets.trim()) {
      alert("Please enter a target to scan");
      return;
    }
    
    const token = localStorage.getItem('accessToken');
    if (!token) {
        alert("Authentication error. Please log in again.");
        return;
    }

    setIsScanning(true);
    setScanMessage("Initiating scan...");

    try {
      const response = await fetch(`${API_BASE_URL}/scans/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ targets: targets.trim() }),
      });

      const data = await response.json();

      if (response.ok) {
        setScanMessage('Scan completed! Found ${data.hosts_discovered || 0} host(s)');
        console.log("Scan result:", data);
        
        setTimeout(() => {
          setTarget("");
          setScanMessage("");
        }, 5000);
      } else {
        if (response.status === 401) {
            setScanMessage('Authentication failed. Please log in again');
        } else {
            setScanMessage('Scan failed: ${data.detail || "Unknown error"}');
        }
      }
    } catch (error) {
      console.error("Scan error:", error);
      setScanMessage(`Error: ${error.message}`);
    } finally {
      setIsScanning(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !isScanning) {
      handleStartScan();
    }
  };
  return (
    <div className="dashboard-container">
      {/* message that displays when the user's email is loaded */}
      {userEmail && <h2 className="welcome-header">Welcome, {userEmail}!</h2>}

      <div className="scan-section">
        <h1>Start a New Scan</h1>
        <div className="scan-input-container">
          <FaBullseye className="scan-input-icon" />
          <input
            type="text"
            className="scan-input"
            placeholder="Enter target (e.g., 10.50.100.0/24, 10.50.100.5)"
            value={targets}
            onChange={(e) => setTarget(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isScanning}
          />
          <button 
            className="scan-button" 
            onClick={handleStartScan}
            disabled={isScanning}
          >
            {isScanning ? "Scanning..." : "Start Scan"}
          </button>
        </div>
        {scanMessage && (
          <div style={{ 
            marginTop: '1rem', 
            padding: '0.75rem', 
            borderRadius: '8px',
            backgroundColor: scanMessage.includes('✓') ? 'rgba(72, 187, 120, 0.2)' : 'rgba(229, 62, 62, 0.2)',
            color: scanMessage.includes('✓') ? '#48bb78' : '#e53e3e',
            border: scanMessage.includes('✓') ? '1px solid #48bb78' : '1px solid #e53e3e'
          }}>
            {scanMessage}
          </div>
        )}
      </div>

      {/* Stats Cards */}
      <div className="stats-section">
        <div className="stat-card">
          <p>Total Assets</p>
          <span>1,204</span>
        </div>
        <div className="stat-card">
          <p>Hosts Online</p>
          <span>987</span>
        </div>
        <div className="stat-card">
          <p>Vulns Found</p>
          <span>312</span>
        </div>
        <div className="stat-card">
          <p>Critical Risks</p>
          <span className="critical-risk">19</span>
        </div>
      </div>

      {/* Recent Scans Table */}
      <div className="recent-scans-section">
        <h2>Recent Scans</h2>
        <table className="scans-table">
          <thead>
            <tr>
              <th>Target</th>
              <th>Status</th>
              <th>Assets Found</th>
              <th>Started</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>10.0.0.0/24</td>
              <td>
                <span className="status-tag completed">Completed</span>
              </td>
              <td>42</td>
              <td>2 hours ago</td>
            </tr>
            <tr>
              <td>scanme.nmap.org</td>
              <td>
                <span className="status-tag in-progress">In Progress</span>
              </td>
              <td>1</td>
              <td>5 minutes ago</td>
            </tr>
            <tr>
              <td>192.168.1.0/24</td>
              <td>
                <span className="status-tag failed">Failed</span>
              </td>
              <td>0</td>
              <td>1 day ago</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Dashboard;