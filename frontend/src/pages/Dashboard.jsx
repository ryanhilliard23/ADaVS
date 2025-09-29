import React from "react";
import { FaBullseye } from 'react-icons/fa';
import "../css/dashboard.css"; 

const Dashboard = () => {
  return (
    <div className="dashboard-container">
      <div className="scan-section">
        <h1>Start a New Scan</h1>
        <div className="scan-input-container">
          <FaBullseye className="scan-input-icon" />
          <input
            type="text"
            className="scan-input"
            placeholder="Enter target (e.g., 192.168.1.0/24, example.com)"
          />
          <button className="scan-button">Start Scan</button>
        </div>
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
          {/* ... table content ... */}
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