#!/bin/sh
set -e

if [ "$(id -u)" -eq 0 ]; then
  ip route add default via 10.50.100.1 dev eth0 || true
fi

exec python -m uvicorn main:app --host 0.0.0.0 --port 8001