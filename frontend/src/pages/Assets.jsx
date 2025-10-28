import React from 'react';
import '../css/assets.css';

const Assets = () => {

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
                <th>Open Ports</th>
                <th>Last Seen</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td data-label="IP Address">10.0.0.5</td>
                <td data-label="Hostname">dc-01.corp.local</td>
                <td data-label="OS">Windows Server 2019</td>
                <td data-label="Open Ports">8</td>
                <td data-label="Last Seen">2 hours ago</td>
              </tr>
              <tr>
                <td data-label="IP Address">10.0.0.12</td>
                <td data-label="Hostname">ubuntu-web.corp.local</td>
                <td data-label="OS">Linux 5.4</td>
                <td data-label="Open Ports">3</td>
                <td data-label="Last Seen">2 hours ago</td>
              </tr>
              <tr>
                <td data-label="IP Address">45.33.32.156</td>
                <td data-label="Hostname">scanme.nmap.org</td>
                <td data-label="OS">Linux 2.6</td>
                <td data-label="Open Ports">5</td>
                <td data-label="Last Seen">5 minutes ago</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Assets;