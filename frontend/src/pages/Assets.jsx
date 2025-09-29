import React, { useState } from 'react';
import '../css/assets.css';

const API_BASE = "http://localhost:8000/api";

const Assets = () => {
  const [assetId, setAssetId] = useState(1);

  // Handler for GET /assets
  const handleGetAssets = async () => {
  try {
    const res = await fetch(`${API_BASE}/assets/`); // <-- add trailing slash
    const data = await res.json();
    console.log("GET /assets/ response:", data);
    alert("Check console for /assets/ response!");
  } catch (err) {
    console.error(err);
    alert("Error fetching assets");
  }
  };

  // Handler for GET /assets/{asset_id}
  const handleGetAssetById = async () => {
    try {
      const res = await fetch(`${API_BASE}/assets/${assetId}`);
      const data = await res.json();
      console.log(`GET /assets/${assetId} response:`, data);
      alert(`Check console for /assets/${assetId} response!`);
    } catch (err) {
      console.error(err);
      alert("Error fetching asset by ID");
    }
  };

  return (
    <div className="assets-container">
      <h1>Discovered Assets</h1>
      <div style={{ marginBottom: "1rem" }}>
        <button onClick={handleGetAssets}>GET /assets</button>
        <input
          type="number"
          value={assetId}
          onChange={e => setAssetId(e.target.value)}
          min={1}
          style={{ margin: "0 8px" }}
        />
        <button onClick={handleGetAssetById}>
          GET /assets/&#123;asset_id&#125;
        </button>
      </div>
      <div className="assets-table-wrapper">
        <table className="assets-table">
          <thead>
            <tr>
              <th>IP Address</th>
              <th>Hostname</th>
              <th>OS</th>
              <th>Open Ports</th>
              <th>Last Seen</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>10.0.0.5</td>
              <td>dc-01.corp.local</td>
              <td>Windows Server 2019</td>
              <td>8</td>
              <td>2 hours ago</td>
            </tr>
            <tr>
              <td>10.0.0.12</td>
              <td>ubuntu-web.corp.local</td>
              <td>Linux 5.4</td>
              <td>3</td>
              <td>2 hours ago</td>
            </tr>
            <tr>
              <td>45.33.32.156</td>
              <td>scanme.nmap.org</td>
              <td>Linux 2.6</td>
              <td>5</td>
              <td>5 minutes ago</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Assets;