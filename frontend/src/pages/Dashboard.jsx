import React, { useState, useEffect, useCallback, useRef } from "react";
import { FaBullseye, FaLock, FaGlobe, FaChevronDown } from "react-icons/fa"; 
import { useOutletContext } from 'react-router-dom'; 
import NotificationManager from '../components/NotificationManager'; 
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
  const { userEmail } = useOutletContext() || {}; 
  const [targets, setTarget] = useState("");
  const [isScanning, setIsScanning] = useState(false);
  const [scanMessage, setScanMessage] = useState("");
  const [scans, setScans] = useState([]);
  const [error, setError] = useState("");

  const [isPublicScan, setIsPublicScan] = useState(() => {
    const savedMode = localStorage.getItem("scanMode");
    return savedMode === "public";
  });

  const [showModeSelector, setShowModeSelector] = useState(false); 
  const [notification, setNotification] = useState(""); 
  const [isWarningDismissed, setIsWarningDismissed] = useState(false); 
  const statusCardRef = useRef(null); 

  const fetchScans = useCallback(async () => {
    try {
      const token = localStorage.getItem("accessToken");
      const res = await fetch(`https://adavs-backend.onrender.com/api/scans/`, {
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
    setIsWarningDismissed(false);
  }, [isPublicScan]);

  useEffect(() => {
    if (isWarningDismissed) {
        setNotification("");
        return;
    }

    if (isPublicScan) {
        setNotification("Basic host and service discovery on any public IP, Domain, or Subnet (CIDR). No vulnerability data is stored.");
    } else {
        setNotification("Full vulnerability detection and data storage. Limited to internal subnets (10.50.100.0/24).");
    }
      
  }, [isPublicScan, isWarningDismissed]); 
  
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        statusCardRef.current &&
        !statusCardRef.current.contains(event.target) &&
        !event.target.closest('.mode-status-card')
      ) {
          setShowModeSelector(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
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

    // Validation for Private Scan mode
    if (!isPublicScan && targets.trim() !== "10.50.100.0/24" && targets.trim() !== "10.50.100.5") {
         alert("For Private Scanning, only the allowed subnet (10.50.100.0/24) or single IP (10.50.100.5) is permitted.");
         return;
    }

    setIsScanning(true);
    setScanMessage(`Initiating ${isPublicScan ? 'Public' : 'Private'} scan...`);

    try {
      const response = await fetch(`https://adavs-backend.onrender.com/api/scans/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ 
            targets: targets.trim(),
            scan_type: isPublicScan ? 'public' : 'private'
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setScanMessage(
          `${isPublicScan ? 'Public Scan' : 'Private Scan'} completed! Found ${data.hosts_discovered || 0} host(s)`
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
          setScanMessage(`${isPublicScan ? 'Public Scan' : 'Private Scan'} failed: ${data.detail || "Unknown error"}`);
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
  
  const handleModeChange = (isPublic) => {
      setIsPublicScan(isPublic);
      localStorage.setItem("scanMode", isPublic ? "public" : "private");
      setShowModeSelector(false); 
  };
  
  const handleWarningDismiss = () => {
      setNotification("");
      setIsWarningDismissed(true); 
  };
  
  const currentMode = isPublicScan ? 'Public' : 'Private';
  const modeIcon = isPublicScan ? <FaGlobe /> : <FaLock />;

  return (
    <div className="dashboard-container">
      
      <NotificationManager 
          message={notification} 
          type={isPublicScan ? 'warning' : 'success'} 
          onClose={handleWarningDismiss} 
      />
      
      <div className="scan-mode-status-container" ref={statusCardRef}>
        <button 
            className={`mode-status-card ${isPublicScan ? 'public-mode' : 'private-mode'}`} 
            onClick={() => setShowModeSelector(prev => !prev)}
            aria-expanded={showModeSelector}
            aria-controls="mode-selector-popover"
            title="Click to switch between Public and Private scanning"
        >
            {modeIcon}
            <span style={{ margin: "0 0.5rem" }}>{currentMode} Scan Mode</span>
            <FaChevronDown className={`dropdown-arrow ${showModeSelector ? 'open' : ''}`} />
        </button>

        {showModeSelector && (
            <div id="mode-selector-popover" className="mode-selector-popover">
                <div className="popover-header">Select Scanning Mode</div>
                
                <button className={`popover-mode-button ${!isPublicScan ? 'active' : ''}`} onClick={() => handleModeChange(false)}>
                    <FaLock />
                    <div>
                        <strong>Private Asset Scan</strong>
                        <p>Full vulnerability detection and data storage. Limited to internal subnets (10.50.100.0/24).</p>
                    </div>
                </button>
                
                <button className={`popover-mode-button ${isPublicScan ? 'active' : ''}`} onClick={() => handleModeChange(true)}>
                    <FaGlobe />
                    <div>
                        <strong>Public Asset Scan</strong>
                        <p>Basic host and service discovery on any public IP, Domain, or Subnet (CIDR). No vulnerability data is stored.</p>
                    </div>
                </button>
            </div>
        )}
      </div>

      <div className="scan-section">
        <h1>Start a New Scan</h1>
        
        <div className="scan-input-container">
          <FaBullseye className="scan-input-icon" />
          <input
            type="text"
            className="scan-input"
            placeholder={isPublicScan ? "Enter public IP, Domain, or Subnet (e.g., 8.8.8.8/24)" : "Enter private target (10.50.100.0/24 or 10.50.100.5)"}
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
        {scanMessage && <div className="scan-message">{scanMessage}</div>} 
      </div>

      <div className="recent-scans-section">
        <h2>Recent Scans</h2>
        <div className="table-scroll-container">
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
                        const target = s.targets || s.target || s.host || s.network || s.name || "unknown";
                        
                        const statusRaw = (s.status || s.state || "").toString().toLowerCase();
                        const status = statusRaw.includes("complete") || statusRaw.includes("done")
                            ? "completed"
                            : statusRaw.includes("progress") || statusRaw.includes("running")
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
    </div>
  );
};

export default Dashboard;