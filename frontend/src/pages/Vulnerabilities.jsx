import React, { useState } from "react";
import "../css/vulnerabilities.css";

const API_BASE = "http://localhost:8000/api";

const Vulnerabilities = () => {
  const [vulnerabilityId, setVulnerabilityId] = useState(1);
  const [serviceId, setServiceId] = useState(1);

  // Handler for GET/vulnerabilities/
  const handleGetVulnerabilities = async () => {
    try {
      const res = await fetch(`${API_BASE}/vulnerabilities/`);
      const data = await res.json();
      console.log("GET/vulnerabilites/ response:", data);
    } catch (err) {
      console.log(err);
      alert("Error fetching vulnerabilities");
    }
  };

  // Handler for GET/vulnerabilities/vuln_id/
  const handleGetVulnerabilityById = async () => {
    try {
      const res = await fetch(`${API_BASE}/vulnerabilities/${vulnerabilityId}`);
      const data = await res.json();
      console.log(`GET/vulnerabilities/${vulnerabilityId}/ response:`, data);
    } catch (err) {
      console.log(err);
      alert("Error fetching vulnerability by id");
    }
  };

  // Handler for GET/vulnerabilities/service_id/
  const handleGetVulnerabilitiesByServiceId = async () => {
    try {
      const res = await fetch(
        `${API_BASE}/vulnerabilities/service/${serviceId}`
      );
      const data = await res.json();
      console.log(`GET/vulnerabilities/service/${serviceId}/ response:`, data);
    } catch (err) {
      console.log(err);
      alert("Error fetching vulnerabilities by service id");
    }
  };

  return (
    <div className="vulnerabilities-container">
      <h1>Vulnerabilities</h1>
      <div className="vulnerabilities-table-wrapper">
        <table className="vulnerabilities-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Severity</th>
              <th>Target</th>
              <th>Detected</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Log4j RCE (CVE-2021-44228)</td>
              <td>
                <span className="severity-critical">Critical</span>
              </td>
              <td>10.0.0.12:8080</td>
              <td>2 hours ago</td>
            </tr>
            <tr>
              <td>Git Config Exposed</td>
              <td>
                <span className="severity-high">High</span>
              </td>
              <td>10.0.0.12:80</td>
              <td>2 hours ago</td>
            </tr>
            <tr>
              <td>TLS Version 1.0/1.1 Supported</td>
              <td>
                <span className="severity-medium">Medium</span>
              </td>
              <td>45.33.32.156:443</td>
              <td>5 minutes ago</td>
            </tr>
            <tr>
              <td>Directory Listing</td>
              <td>
                <span className="severity-low">Low</span>
              </td>
              <td>10.0.0.12:80</td>
              <td>2 hours ago</td>
            </tr>
          </tbody>
        </table>
      </div>
      {/* This div can be deleted or changed only used for temporary buttons for endpoints*/}
      <div>
        <button onClick={handleGetVulnerabilities}>Get Vulnerabilities</button>
        <input
          type="number"
          value={vulnerabilityId}
          onChange={(e) => setVulnerabilityId(e.target.value)}
          min={1}
        ></input>
        <button onClick={handleGetVulnerabilityById}>
          Get Vulnerability By Id
        </button>
        <input
          type="number"
          value={serviceId}
          onChange={(e) => setServiceId(e.target.value)}
          min={1}
        ></input>
        <button onClick={handleGetVulnerabilitiesByServiceId}>
          Get Vulnerability By Service Id
        </button>
      </div>
    </div>
  );
};

export default Vulnerabilities;
