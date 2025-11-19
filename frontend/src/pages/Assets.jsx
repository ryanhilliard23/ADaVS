import React, { useEffect, useState } from "react";
import "../css/assets.css";
import BannerPreview from "../components/BannerPreview";

const Assets = () => {
  const [asset, setAsset] = useState([]);
  const [loading, setLoading] = useState(false);
  const [previewBanner, setPreviewBanner] = useState(null);

  useEffect(() => {
    handleGetAssets();
  }, []);

  const handleGetAssets = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("accessToken");
      const res = await fetch("https://adavs-backend.onrender.com/api/assets/", {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      });

      if (!res.ok) {
        throw new Error(`HTTP error! Status: ${res.status}`);
      }

      const data = await res.json();

      const processed = data.map(a => ({
        ...a,
        services: a.services.map(s => ({
          ...s,
          short_banner: getShortBanner(s.banner),
        })),
      }));

      setAsset(processed);

    } catch (err) {
      console.error(err);
      alert("Error fetching assets");
    } finally {
      setLoading(false);
    }
  };

  const getShortBanner = (banner) => {
    if (!banner) return "—";
    const trimmed = banner.trim();
    if (trimmed.length <= 40) return trimmed;
    return trimmed.slice(0, 40) + "...";
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
                <th className="banner-cell">Banner</th>
              </tr>
            </thead>

            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="6" style={{ textAlign: "center" }}>
                    Loading...
                  </td>
                </tr>
              ) : asset.length === 0 ? (
                <tr>
                  <td colSpan="6" style={{ textAlign: "center" }}>
                    No assets found
                  </td>
                </tr>
              ) : (
                asset.flatMap((a) =>
                  a.services.length > 0
                    ? a.services.map((s) => (
                        <tr key={`${a.id}-${s.id}`}>
                          <td data-label="IP Address">{a.ip_address}</td>
                          <td data-label="Hostname">
                            {a.hostname || a.ip_address}
                          </td>
                          <td data-label="OS">{a.os || "—"}</td>
                          <td data-label="Port">{s.port}</td>
                          <td data-label="Service Name">
                            {s.service_name || "—"}
                          </td>
                          <td data-label="Banner" className="banner-cell">
                            {s.banner ? (
                              <span
                                className="banner-preview-link"
                                onClick={() => setPreviewBanner(s.banner)}
                              >
                                {s.short_banner}
                              </span>
                            ) : (
                              "—"
                            )}
                          </td>
                        </tr>
                      ))
                    : [
                        <tr key={a.id}>
                          <td data-label="IP Address">{a.ip_address}</td>
                          <td data-label="Hostname">
                            {a.hostname || "—"}
                          </td>
                          <td data-label="OS">{a.os || "—"}</td>
                          <td
                            colSpan="3"
                            style={{ textAlign: "center", color: "#888" }}
                          >
                            No services
                          </td>
                        </tr>,
                      ]
                )
              )}
            </tbody>
          </table>
        </div>
      </div>

      {previewBanner && (
        <BannerPreview
          banner={previewBanner}
          onClose={() => setPreviewBanner(null)}
        />
      )}
    </div>
  );
};

export default Assets;
