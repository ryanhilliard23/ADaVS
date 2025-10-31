import React, { useState, useEffect } from "react";
import "../css/vulnerabilities.css";

const Vulnerabilities = () => {
  const [vulnerabilities, setVulnerabilities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchVulnerabilities = async () => {
      try {
        const token = localStorage.getItem("accessToken");
        const response = await fetch("/api/vulnerabilities/", {
          headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        setVulnerabilities(data);
      } catch (e) {
        console.error("Failed to fetch vulnerabilities:", e);
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };

    fetchVulnerabilities();
  }, []);

  const renderSeverityTag = (severity) => {
    if (!severity) return null;
    const severityClass = `severity-${severity.toLowerCase()}`;
    return <span className={severityClass}>{severity}</span>;
  };

  return (
    <div className="vulnerabilities-container">
      <h1>Vulnerabilities</h1>
      <div className="vulnerabilities-table-wrapper">
        <div className="table-scroll-container">
          <table className="vulnerabilities-table">
            <thead>
              <tr>
                <th>Severity</th>
                <th>Vulnerability</th>
                <th>Description</th>
                <th>Evidence</th>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr>
                  <td colSpan="4" style={{ textAlign: "center" }}>
                    Loading vulnerabilities...
                  </td>
                </tr>
              )}
              {error && (
                <tr>
                  <td colSpan="4" style={{ textAlign: "center", color: "red" }}>
                    Error: {error}
                  </td>
                </tr>
              )}
              {!loading && !error && vulnerabilities.length === 0 && (
                <tr>
                  <td colSpan="4" style={{ textAlign: "center" }}>
                    No vulnerabilities found.
                  </td>
                </tr>
              )}
              {!loading &&
                !error &&
                vulnerabilities.map((vuln) => (
                  <tr key={vuln.id}>
                    <td data-label="Severity">
                      {renderSeverityTag(vuln.severity)}
                    </td>
                    <td data-label="Vulnerability">{vuln.template_id}</td>
                    <td data-label="Description">
                      {vuln.description || "N/A"}
                    </td>
                    <td data-label="Evidence">
                      <span>{vuln.evidence || "N/A"}</span>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Vulnerabilities;