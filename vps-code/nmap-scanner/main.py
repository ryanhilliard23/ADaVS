from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import subprocess
import json
import os

app = FastAPI(title="Remote Nuclei Runner")

NUCLEI_TOKEN = os.getenv("NUCLEI_TOKEN")

class TargetItem(BaseModel):
    target: str
    tags: Optional[str] = None

class ScanRequest(BaseModel):
    targets: List[TargetItem]

@app.post("/scan")
async def scan(req: ScanRequest, request: Request):

    token = request.headers.get("X-Scanner-Token")
    if token != NUCLEI_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

    if not req.targets:
        raise HTTPException(status_code=400, detail="No targets provided")

    all_results = []


    print("DEBUGGING 5")
    print("req.targets")
    for item in req.targets:
        target = (item.target or "").strip()
        if not target:
            continue


        cmd = [
            "nuclei",
            "-target", target,
            "-t", "/home/nuclei/nuclei-templates",
            "-jsonl", "-silent", "-no-color",
            "-severity", "low,medium,high,critical",
            "-duc", "-rate-limit", "1500",
            "-c", "30", "-timeout", "3",
            "-bulk-size", "150", "-retries", "1"
        ]


        if item.tags:

            cmd.extend(["-tags", item.tags.strip().lower()])

        print(f"[DEBUG] Running command for {target}: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=900
            )
            print("DEBUGGING RESULT")
            print(result)

            for line in result.stdout.splitlines():
                try:
                    parsed = json.loads(line)
                    print("DEBUGGING PARSED")
                    print(parsed)
                    all_results.append(parsed)
                except json.JSONDecodeError:
                    if line.strip():
                        print(f"[WARN] Non-JSON line: {line.strip()}")

            if result.stderr.strip():
                print(f"[NUCLEI STDERR] ({target}) {result.stderr.strip()}")

        except subprocess.TimeoutExpired:
            print(f"[ERROR] Timeout for {target}")
        except Exception as e:
            print(f"[ERROR] Exception running nuclei for {target}: {e}")

    print(f"[SUMMARY] Collected {len(all_results)} total results from all targets.")
    return all_results