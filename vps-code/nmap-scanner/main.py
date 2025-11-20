from fastapi import FastAPI, HTTPException, Header, Depends, status
from pydantic import BaseModel
import subprocess
import ipaddress
import os
import secrets
from typing import Optional

app = FastAPI(title="ADaVS Scanner Service")

ALLOWED_SUBNETS = ["10.50.100.0/24"]

class ScanRequest(BaseModel):
    targets: list[str]

def validate_targets(targets: list[str]):
    networks = [ipaddress.ip_network(s) for s in ALLOWED_SUBNETS]

    print("TEST 2")

    for t in targets:
        try:
            if "/" in t:
                net = ipaddress.ip_network(t, strict=False)
                if not any(net.subnet_of(a) for a in networks):
                    raise ValueError(f"{t} not allowed")
            else:
                ip = ipaddress.ip_address(t)
                if not any(ip in a for a in networks):
                    raise ValueError(f"{t} not allowed")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

def verify_scanner_token(x_scanner_token: Optional[str] = Header(None)):
    expected = os.environ.get("SCANNER_TOKEN")
    if not expected:
        # Fail closed if token not configured
        raise HTTPException(status_code=500, detail="Server missing scanner token configuration")
    if not x_scanner_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing scanner token")
    if not secrets.compare_digest(x_scanner_token, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scanner token")
    return True

NMAP_CMD_BEST = [
    "nmap",
    "-Pn",
    "-sS",
    "-sV",
    "-O",
    "-p-",
    "-T5",
    "--max-retries", "2",
    "--host-timeout", "10m",
    "--reason",
    "--open",
    "-oX", "-",
]

@app.post("/scan")
def run_scan(req: ScanRequest, _ok: bool = Depends(verify_scanner_token)):
    validate_targets(req.targets)

    cmd = NMAP_CMD_BEST + req.targets
    print("TEST 3")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60*60)
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Scan timed out")
    print("TEST 4")
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr or "nmap failed")

    MAX_MB = 50
    xml_bytes = result.stdout.encode("utf-8")
    if len(xml_bytes) > MAX_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Scan output too large; store to object storage instead")

    return {"xml": result.stdout}

@app.get("/")
async def health():
    return {"status": "ok", "message": "Nmap scanner is live"}