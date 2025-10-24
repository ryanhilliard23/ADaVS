import React from "react";
import "../css/vulnerabilities.css";

const Vulnerabilities = () => {

  return (
    <div className="vulnerabilities-container">
      <h1>Vulnerabilities</h1>
      <div className="vulnerabilities-table-wrapper">
        <div className="table-scroll-container">
          <table className="vulnerabilities-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Severity</th>
                <th>Target</th>
                <th>Detected</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Log4j RCE (CVE-2021-44228)</td>
                <td>
                  <span className="severity-critical">Critical</span>
                </td>
                <td>10.0.0.12:8080</td>
                <td>2 hours ago</td>
              </tr>
              <tr>
                <td>Git Config Exposed</td>
                <td>
                  <span className="severity-high">High</span>
                </td>
                <td>10.0.0.12:80</td>
                <td>2 hours ago</td>
              </tr>
              <tr>
                <td>TLS Version 1.0/1.1 Supported</td>
                <td>
                  <span className="severity-medium">Medium</span>
                </td>
                <td>45.33.32.156:443</td>
                <td>5 minutes ago</td>
              </tr>
              <tr>
                <td>Directory Listing</td>
                <td>
                  <span className="severity-low">Low</span>
                </td>
                <td>10.0.0.12:80</td>
                <td>2 hours ago</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Vulnerabilities;