import React from 'react';
import { MdClose, MdWarning, MdInfo } from 'react-icons/md';
import '../css/dashboard.css'; 

const NotificationManager = ({ message, type = 'warning', onClose }) => {
  if (!message) return null;

  const getNotificationClass = () => {
    switch (type) {
      case 'warning':
        return 'notification-warning';
      case 'success':
        return 'notification-success';
      case 'error':
        return 'notification-error';
      default:
        return 'notification-info';
    }
  };

  // Choose icon based on type
  const Icon = type === 'warning' ? MdWarning : MdInfo;

  return (
    <div className={`notification-bar ${getNotificationClass()}`}>
      <Icon className="notification-icon" />
      <span className="notification-message">{message}</span>
      <button className="notification-close-button" onClick={onClose} aria-label="Dismiss notification">
        <MdClose />
      </button>
    </div>
  );
};

export default NotificationManager;