# ADaVS Infrastructure & VPS Setup

This directory contains the infrastructure code for the ADaVS (Asset Discovery and Vulnerability Scanning) system.

## Architecture

The VPS uses a **Hybrid Network** approach:
1.  **Vulnerable Assets:** Managed via Docker Compose on an isolated Macvlan subnet.
2.  **Scanners:** Managed via manual Docker scripts to attach to **both** the Bridge network (for internet/management) and Macvlan (for scanning).

* **Subnet:** `10.50.100.0/24`
* **Gateway:** `10.50.100.1`
* **Ingress:** Traffic enters VPS on ports `8000` & `8001` -> Proxied to Macvlan IPs.

---

## 📋 IP Address & Port Map

| Service               | IP Address        | Host Port | Notes |
| **Nmap Scanner**      | `10.50.100.250`   | `8000`    | Requires Root & Net Admin |
| **Nuclei Scanner**    | `10.50.100.251`   | `8001`    | Requires Root & Net Admin |
| **Vuln FTP**          | `10.50.100.50`    | N/A       | Deployed via Compose |
| **Vuln Redis**        | `10.50.100.51`    | N/A       | Deployed via Compose |

---

## 🛠️ Deployment Steps

### 1. Initial Network Setup
The Macvlan network must be created once before running anything.
*(Replace `eth0` with your main interface if different).*

```bash
docker network create -d macvlan \
  --subnet=10.50.100.0/24 \
  --gateway=10.50.100.1 \
  -o parent=eth0 \
  adavs_macvlan

2. Deploy Vulnerable Assets
Start the FTP, Redis, and other intentional vulnerabilities.

Bash

docker-compose up -d

3. Start the Scanners
We use helper scripts to build the scanners and attach them to the correct networks with Root privileges.

Bash

# Make scripts executable
chmod +x scripts/*.sh

# Start Nmap Scanner (10.50.100.250)
./scripts/start_nmap.sh

# Start Nuclei Scanner (10.50.100.251)
./scripts/start_nuclei.sh
🔗 Connectivity & Security
1. Socat Proxy (Required)
The Host cannot reach Macvlan IPs directly. You must run socat to bridge the connection.

Bash

# Nmap Proxy (Host 8000 -> 10.50.100.250)
sudo nohup socat TCP4-LISTEN:8000,fork,reuseaddr TCP4:10.50.100.250:8000 &

# Nuclei Proxy (Host 8001 -> 10.50.100.251)
sudo nohup socat TCP4-LISTEN:8001,fork,reuseaddr TCP4:10.50.100.251:8001 &
2. Firewall Rules (Iptables)
These rules restrict access to the scanner ports (8000/8001). Only the Render Backend subnets and specific Admin IPs are allowed.

Run these commands to restore the security policy:

Bash

# 1. Allow Render Backend Subnets (Nmap & Nuclei ports)
iptables -A INPUT -s 216.24.60.0/24 -p tcp -m tcp --dport 8000 -j ACCEPT
iptables -A INPUT -s 216.24.60.0/24 -p tcp -m tcp --dport 8001 -j ACCEPT

iptables -A INPUT -s 74.220.49.0/24 -p tcp -m tcp --dport 8000 -j ACCEPT
iptables -A INPUT -s 74.220.49.0/24 -p tcp -m tcp --dport 8001 -j ACCEPT

iptables -A INPUT -s 74.220.57.0/24 -p tcp -m tcp --dport 8000 -j ACCEPT
iptables -A INPUT -s 74.220.57.0/24 -p tcp -m tcp --dport 8001 -j ACCEPT

# 2. Reject all other traffic to scanner ports
iptables -A INPUT -p tcp -m tcp --dport 8000 -j REJECT --reject-with tcp-reset
iptables -A INPUT -p tcp -m tcp --dport 8001 -j REJECT --reject-with tcp-reset

# 3. Persist Rules
netfilter-persistent save
Debugging
View Logs:

docker logs scanner --tail 50

docker logs nuclei-runner --tail 50

Check Network: 
docker network inspect adavs_macvlan