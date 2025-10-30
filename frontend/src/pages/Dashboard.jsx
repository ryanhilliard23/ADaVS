import React, { useState, useEffect, useCallback } from "react";
import { FaBullseye } from "react-icons/fa";
import "../css/dashboard.css";

function relativeTimeFromISO(iso) {
  try {
    const d = new Date(iso);
    const now = Date.now();
    const diff = Math.floor((now - d.getTime()) / 1000);
    if (isNaN(diff)) return iso;
    if (diff < 60) return `${diff} seconds ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)} minutes ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
    return `${Math.floor(diff / 86400)} days ago`;
  } catch {
    return iso;
  }
}

const Dashboard = () => {
  const [targets, setTarget] = useState("");
  const [isScanning, setIsScanning] = useState(false);
  const [scanMessage, setScanMessage] = useState("");
  const [userEmail, setUserEmail] = useState("");
  const [scans, setScans] = useState([]);
  const [error, setError] = useState("");

  const fetchScans = useCallback(async () => {
    try {
      const token = localStorage.getItem("accessToken");
      const res = await fetch(`/api/scans/`, {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      });

      if (!res.ok) {
        throw new Error(`HTTP error! Status: ${res.status}`);
      }
      
      const data = await res.json();
      
      let normalized = Array.isArray(data)
        ? data
        : data?.scans || data?.results || data?.data || [];
      if (!Array.isArray(normalized)) normalized = [];

      setScans(normalized);
      setError("");
    } catch (e) {
      console.error("Failed to fetch scans:", e);
      setError("Error loading scans");
    }
  }, []);

  useEffect(() => {
    const fetchUserData = async () => {
      const token = localStorage.getItem("accessToken");
      if (!token) return;

      try {
        const response = await fetch(`/api/users/me`, {
          headers: { Authorization: `Bearer ${token}` },
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
  }, []);

  useEffect(() => {
    fetchScans();
  }, [fetchScans]);

  const handleStartScan = async () => {
    if (!targets.trim()) {
      alert("Please enter a target to scan");
      return;
    }
    const token = localStorage.getItem("accessToken");
    if (!token) {
      alert("Authentication error. Please log in again.");
      return;
    }

    setIsScanning(true);
    setScanMessage("Initiating scan...");

    try {
      const response = await fetch(`/api/scans/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ targets: targets.trim() }),
      });

      const data = await response.json();

      if (response.ok) {
        setScanMessage(
          `Scan completed! Found ${data.hosts_discovered || 0} host(s)`
        );

        fetchScans();
        
        setTimeout(() => {
          setTarget("");
          setScanMessage("");
        }, 5000);
      } else {
        if (response.status === 401) {
          setScanMessage("Authentication failed. Please log in again");
        } else {
          setScanMessage(`Scan failed: ${data.detail || "Unknown error"}`);
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
    if (e.key === "Enter" && !isScanning) {
      handleStartScan();
    }
  };

  return (
    <div className="dashboard-container">
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
        {scanMessage && <div>{scanMessage}</div>}
      </div>

      <div className="recent-scans-section">
        <h2>Recent Scans</h2>
        <table className="scans-table">
          <thead>
            <tr>
              <th>Target</th>
              <th>Status</th>
              <th>Started</th>
            </tr>
          </thead>
          <tbody>
            {error ? (
              <tr>
                <td colSpan={3}>Error loading scans</td>
              </tr>
            ) : scans.length === 0 ? (
              <tr>
                <td colSpan={3}>No scans found</td>
              </tr>
            ) : (
              scans.map((s, idx) => {
                const target =
                  s.targets ||
                  s.target ||
                  s.host ||
                  s.network ||
                  s.name ||
                  "unknown";
                
                const statusRaw = (s.status || s.state || "")
                  .toString()
                  .toLowerCase();
                const status =
                  statusRaw.includes("complete") || statusRaw.includes("done")
                    ? "completed"
                    : statusRaw.includes("progress") ||
                      statusRaw.includes("running")
                    ? "in-progress"
                    : statusRaw || "failed";

                const time = s.started_at
                  ? relativeTimeFromISO(s.started_at)
                  : s.finished_at
                  ? relativeTimeFromISO(s.finished_at)
                  : "unknown";

                return (
                  <tr key={s.id ?? idx}>
                    <td data-label="Target">{target}</td>
                    <td data-label="Status">
                      <span className={`status-tag ${status}`}>
                        {status.replace("-", " ")}
                      </span>
                    </td>
                    <td data-label="Started">{time}</td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Dashboard;