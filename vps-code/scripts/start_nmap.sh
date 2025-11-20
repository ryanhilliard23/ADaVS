#!/bin/bash

cd "$(dirname "$0")/.." || exit

echo "[+] Stopping and removing old Nmap Scanner..."
docker stop scanner 2>/dev/null
docker rm scanner 2>/dev/null

echo "[+] Building Nmap Scanner image..."
cd nmap-scanner
docker build -t scanner:latest .
cd ..

echo "[+] Starting Nmap Scanner (Bridge Mode)..."

docker run -d \
  --name scanner \
  --user root \
  --cap-drop=ALL \
  --cap-add=NET_RAW \
  --cap-add=NET_ADMIN \
  --security-opt=no-new-privileges:true \
  --read-only \
  --tmpfs /tmp:rw,size=200m \
  --tmpfs /run:rw,size=50m \
  --pids-limit=200 \
  --memory=512m \
  --cpus="1" \
  --restart unless-stopped \
  --env-file .env \
  --network bridge \
  scanner:latest

echo "[+] Connecting Nmap Scanner to Macvlan (IP: 10.50.100.250)..."
docker network connect --ip 10.50.100.250 adavs_macvlan scanner

echo "[+] Nmap Scanner is running!"