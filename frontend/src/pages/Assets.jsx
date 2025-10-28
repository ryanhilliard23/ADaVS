import React, { useEffect, useState } from "react";
import "../css/assets.css";

const Assets = () => {
  const [assetId, setAssetId] = useState(1);
  const [asset, setAsset] = useState([]);
  const [loading, setLoading] = useState(false);

  // Show assets on mount
  useEffect(() => {
    handleGetAssets();
  }, []);

  // Handler for GET /assets
  const handleGetAssets = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/assets/`);
      if (!res.ok) {
        throw new Error(`HTTP error! Status: ${res.status}`);
      }

      const data = await res.json();
      setAsset(data);
      console.log(data);
      return data;
    } catch (err) {
      console.error(err);
      setError(err.message);
      alert("Error fetching assets");
    } finally {
      setLoading(false);
    }
  };

  // Handler for GET /assets/{asset_id}
  const handleGetAssetById = async () => {
    try {
      const res = await fetch(`${API_BASE}/assets/${assetId}`);
      const data = await res.json();
      console.log(`GET /assets/${assetId} response:`, data);
    } catch (err) {
      console.error(err);
      alert("Error fetching asset by ID");
    }
  };

  return (
    <div className="assets-container">
      <h1>Discovered Assets</h1>
      <div className="assets-table-wrapper">
        <div className="table-scroll-container">
          <table className="assets-table">
            <thead>
              <tr>
                <th>IP Address</th>
                <th>Hostname</th>
                <th>OS</th>
                <th>Port</th>
                <th>Service Name</th>
                <th>Banner</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>Loading...</tr>
              ) : asset.length === 0 ? (
                <tr>
                  <td>No assets found</td>
                </tr>
              ) : (
                asset.flatMap((a) =>
                  a.services.length > 0
                    ? a.services.map((s) => (
                        <tr key={`${a.id}-${s.id}`}>
                          <td>{a.ip_address}</td>
                          {/* if no hostname, use IP address */}
                          <td>{a.hostname || a.ip_address}</td>
                          <td>{a.os}</td>
                          <td>{s.port}</td>
                          <td>{s.service_name}</td>
                          <td>{s.banner || "—"}</td>
                        </tr>
                      ))
                    : [
                        <tr key={a.id}>
                          <td>{a.ip_address}</td>
                          <td>{a.hostname}</td>
                          <td>{a.os}</td>
                          <td colSpan="3" style={{ color: "#888" }}>
                            No services
                          </td>
                        </tr>,
                        s,
                      ]
                )
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Assets;
