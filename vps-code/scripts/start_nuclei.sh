#!/bin/bash

cd "$(dirname "$0")/.." || exit

echo "[+] Stopping and removing old Nuclei Scanner..."
docker stop nuclei-runner 2>/dev/null
docker rm nuclei-runner 2>/dev/null

echo "[+] Building Nuclei Scanner image..."
cd nuclei-scanner
docker build --no-cache -t nuclei-runner:latest .
cd ..

echo "[+] Starting Nuclei Scanner (Bridge Mode)..."

docker run -d \
  --name nuclei-runner \
  --network bridge \
  --cap-add=NET_RAW --cap-add=NET_ADMIN \
  --security-opt no-new-privileges:true \
  --memory=1.2g --cpus="1" \
  --ulimit nofile=65535:65535 \
  --tmpfs /tmp:rw,size=200m \
  --tmpfs /run:rw,size=50m \
  --env-file .env \
  --user root \
  --restart unless-stopped \
  nuclei-runner:latest

echo "[+] Connecting Nuclei Scanner to Macvlan (IP: 10.50.100.251)..."
docker network connect --ip 10.50.100.251 adavs_macvlan nuclei-runner

echo "[+] Nuclei Scanner is running!"