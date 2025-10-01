import React, { useState } from "react";
import "../css/scans.css";

const API_BASE = "http://localhost:8000/api";

const Scans = () => {
  const [scanId, setScanId] = useState(1);
  const [target, setTarget] = useState("");

  // GET /scans/
  const handleGetScans = async () => {
    try {
      const res = await fetch(`${API_BASE}/scans/`); // trailing slash matches style
      const data = await res.json();
      console.log("GET /scans/ response:", data);
    } catch (err) {
      console.log(err);
      alert("Error fetching scans");
    }
  };

  // GET /scans/{scan_id}
  const handleGetScanById = async () => {
    try {
      const res = await fetch(`${API_BASE}/scans/${scanId}`);
      const data = await res.json();
      console.log(`GET /scans/${scanId} response:`, data);
    } catch (err) {
      console.log(err);
      alert("Error fetching scan by id");
    }
  };

  // POST /scans/ (start new scan)
  const handleStartScan = async () => {
    try {
      const res = await fetch(`${API_BASE}/scans/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target }), // e.g., "192.168.1.0/24" or "scanme.nmap.org"
      });
      const data = await res.json();
      console.log("POST /scans/ response:", data);
    } catch (err) {
      console.log(err);
      alert("Error starting scan");
    }
  };

  return (
    <div className="scans-container">
      <h1>Scans</h1>

      <div className="scans-table-wrapper">
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
            {/* Demo rows to mirror Vulnerabilities page behavior */}
            <tr>
              <td>10.0.0.0/24</td>
              <td>
                <span className="status-completed">Completed</span>
              </td>
              <td>42</td>
              <td>2 hours ago</td>
            </tr>
            <tr>
              <td>scanme.nmap.org</td>
              <td>
                <span className="status-progress">In Progress</span>
              </td>
              <td>1</td>
              <td>5 minutes ago</td>
            </tr>
            <tr>
              <td>192.168.1.0/24</td>
              <td>
                <span className="status-failed">Failed</span>
              </td>
              <td>0</td>
              <td>1 day ago</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Temporary endpoint test buttons (same pattern as Vulnerabilities) */}
      <div style={{ marginTop: "1rem" }}>
        <button onClick={handleGetScans}>Get Scans</button>

        <input
          type="number"
          value={scanId}
          onChange={(e) => setScanId(e.target.value)}
          min={1}
          style={{ margin: "0 8px" }}
        />
        <button onClick={handleGetScanById}>Get Scan By Id</button>

        <input
          type="text"
          value={target}
          onChange={(e) => setTarget(e.target.value)}
          placeholder="Target (e.g., 192.168.1.0/24)"
          style={{ margin: "0 8px" }}
        />
        <button onClick={handleStartScan}>Start Scan</button>
      </div>
    </div>
  );
};

export default Scans;
