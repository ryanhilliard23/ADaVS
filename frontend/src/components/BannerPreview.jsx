import React, { useEffect } from "react";
import "../css/bannerPreview.css";

const BannerPreview = ({ banner, onClose }) => {
  useEffect(() => {
    const handler = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  return (
    <div className="banner-modal-overlay" onClick={onClose}>
      <div className="banner-modal" onClick={(e) => e.stopPropagation()}>
        <div className="banner-modal-header">
          <h2>Service Banner</h2>
          <button className="banner-modal-close" onClick={onClose}>
            ✕
          </button>
        </div>

        <pre className="banner-modal-content">
          {banner}
        </pre>
      </div>
    </div>
  );
};

export default BannerPreview;
