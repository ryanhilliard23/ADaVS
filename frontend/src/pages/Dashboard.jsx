import React, { useState, useEffect } from "react";
import { FaBullseye } from "react-icons/fa";
import "../css/dashboard.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const Dashboard = () => {
  const [targets, setTarget] = useState("");
  const [isScanning, setIsScanning] = useState(false);
  const [scanMessage, setScanMessage] = useState("");
  const [userEmail, setUserEmail] = useState("");
  const [stats, setStats] = useState(null);
  const [recentScans, setRecentScans] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchUserData = async () => {
      const token = localStorage.getItem("accessToken");
      if (!token) return;
      try {
        const res = await fetch(`${API_BASE_URL}/users/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setUserEmail(data.email);
        }
      } catch (err) {
        console.error("Error fetching user data:", err);
      }
    };
    fetchUserData();
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem("accessToken");
      if (!token) return;
      try {
        const [scansRes] = await Promise.all([
          fetch(`${API_BASE_URL}/scans/`, {
            headers: { Authorization: `Bearer ${token}` },
          }),
        ]);
        if (scansRes.ok) {
          const scans = await scansRes.json();
          setRecentScans(Array.isArray(scans) ? scans : []);
        } else {
          setRecentScans([]);
        }
      } catch (err) {
        setError(err.message || "Failed to load data");
      }
    };
    fetchData();
  }, []);

  useEffect(() => {
    const fetchStats = async () => {
      const token = localStorage.getItem("accessToken");
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      const tryFetch = async (paths) => {
        for (const p of paths) {
          try {
            const r = await fetch(`${API_BASE_URL}${p}`, { headers });
            if (r.ok) return r;
          } catch {}
        }
        return null;
      };

      const parseCountish = async (res) => {
        if (!res) return 0;
        let data;
        try {
          data = await res.json();
        } catch {
          return 0;
        }
        if (typeof data === "number") return data;
        if (Array.isArray(data)) return data.length;
        if (data && typeof data.count === "number") return data.count;
        if (data && typeof data.total === "number") return data.total;
        for (const k of [
          "items",
          "results",
          "assets",
          "vulnerabilities",
          "data",
          "records",
          "rows",
        ]) {
          const v = data?.[k];
          if (Array.isArray(v)) return v.length;
          if (v && typeof v.count === "number") return v.count;
          if (Array.isArray(v?.items)) return v.items.length;
        }
        return 0;
      };

      const parseArray = async (res) => {
        if (!res) return [];
        let data;
        try {
          data = await res.json();
        } catch {
          return [];
        }
        if (Array.isArray(data)) return data;
        for (const k of [
          "items",
          "results",
          "assets",
          "vulnerabilities",
          "data",
          "records",
          "rows",
        ]) {
          if (Array.isArray(data?.[k])) return data[k];
          if (Array.isArray(data?.[k]?.items)) return data[k].items;
        }
        return [];
      };

      const assetsRes =
        (await tryFetch(["/assets/", "/assets"])) ||
        (await tryFetch(["/assets/count"]));

      const vulnsRes =
        (await tryFetch(["/vulnerabilities/", "/vulnerabilities"])) ||
        (await tryFetch(["/vulnerabilities/count"]));

      const assetsList =
        assetsRes &&
        (assetsRes.url.endsWith("/assets") ||
          assetsRes.url.endsWith("/assets/"))
          ? await parseArray(assetsRes)
          : [];

      const vulnsList =
        vulnsRes &&
        (vulnsRes.url.endsWith("/vulnerabilities") ||
          vulnsRes.url.endsWith("/vulnerabilities/"))
          ? await parseArray(vulnsRes)
          : [];

      const totalAssets = assetsList.length || (await parseCountish(assetsRes));

      const hostsOnline = totalAssets;

      const vulnsFound = vulnsList.length || (await parseCountish(vulnsRes));

      const criticalRisks = vulnsList.filter((v) => {
        const sev = (v?.severity ?? "").toString().trim().toLowerCase();
        if (sev === "critical" || sev === "high") return true;
        const n = parseInt(sev, 10);
        return Number.isFinite(n) && n >= 4;
      }).length;

      setStats({
        total_assets: totalAssets,
        hosts_online: hostsOnline,
        vulns_found: vulnsFound,
        critical_risks: criticalRisks,
      });
    };

    fetchStats();
  }, []);

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
      const response = await fetch(`${API_BASE_URL}/scans/`, {
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
          `\u2713 Scan completed! Found ${data.hosts_discovered || 0} host(s)`
        );
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
      setScanMessage(`Error: ${error.message}`);
    } finally {
      setIsScanning(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !isScanning) handleStartScan();
  };

  return (
    <div className="dashboard-container">
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
          <div
            style={{
              marginTop: "1rem",
              padding: "0.75rem",
              borderRadius: "8px",
              backgroundColor: scanMessage.includes("\u2713")
                ? "rgba(72, 187, 120, 0.2)"
                : "rgba(229, 62, 62, 0.2)",
              color: scanMessage.includes("\u2713") ? "#48bb78" : "#e53e3e",
              border: scanMessage.includes("\u2713")
                ? "1px solid #48bb78"
                : "1px solid #e53e3e",
            }}
          >
            {scanMessage}
          </div>
        )}
        {error && (
          <div className="alert error" role="alert" style={{ marginTop: 12 }}>
            {error}
          </div>
        )}
      </div>
      <div className="stats-section">
        <div className="stat-card">
          <p>Total Assets</p>
          <span>{stats?.total_assets ?? "\u2014"}</span>
        </div>
        <div className="stat-card">
          <p>Hosts Online</p>
          <span>{stats?.hosts_online ?? "\u2014"}</span>
        </div>
        <div className="stat-card">
          <p>Vulns Found</p>
          <span>{stats?.vulns_found ?? "\u2014"}</span>
        </div>
        <div className="stat-card">
          <p>Critical Risks</p>
          <span className="critical-risk">
            {stats?.critical_risks ?? "\u2014"}
          </span>
        </div>
      </div>
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
            {recentScans.length === 0 ? (
              <tr>
                <td colSpan="4" style={{ textAlign: "center", padding: 16 }}>
                  No recent scans
                </td>
              </tr>
            ) : (
              recentScans.map((scan) => (
                <tr key={scan.id}>
                  <td>{scan.targets}</td>
                  <td>
                    <span
                      className={`status-tag ${String(
                        scan.status
                      ).toLowerCase()}`}
                    >
                      {scan.status}
                    </span>
                  </td>
                  <td>{Array.isArray(scan.assets) ? scan.assets.length : 0}</td>
                  <td
                    title={
                      scan.started_at
                        ? new Date(scan.started_at).toLocaleString()
                        : ""
                    }
                  >
                    {scan.started_at
                      ? new Date(scan.started_at).toLocaleString()
                      : "\u2014"}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Dashboard;
