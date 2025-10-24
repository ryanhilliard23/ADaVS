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
                <td>10.0.0.5</td>
                <td>dc-01.corp.local</td>
                <td>Windows Server 2019</td>
                <td>8</td>
                <td>2 hours ago</td>
              </tr>
              <tr>
                <td>10.0.0.12</td>
                <td>ubuntu-web.corp.local</td>
                <td>Linux 5.4</td>
                <td>3</td>
                <td>2 hours ago</td>
              </tr>
              <tr>
                <td>45.33.32.156</td>
                <td>scanme.nmap.org</td>
                <td>Linux 2.6</td>
                <td>5</td>
                <td>5 minutes ago</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Assets;