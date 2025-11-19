import os
import requests

CENSYS_API_KEY = os.getenv("CENSYS_API_KEY")

BASE_URL = "https://api.platform.censys.io/v3"

class CensysError(Exception):
    pass

def censys_get_host(ip: str):
    if not CENSYS_API_KEY:
        print("[Censys] API Key missing. Skipping.")
        return None

    url = f"{BASE_URL}/global/asset/host/{ip}"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {CENSYS_API_KEY}",
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)

        if r.status_code == 404:
            return None

        if r.status_code == 401:
            print("[Censys] 401 Unauthorized. Check your token permissions.")
            return None

        if r.status_code != 200:
            print(f"[Censys] Error {r.status_code}: {r.text[:200]}")
            return None

        data = r.json()

        if "result" not in data:
            return None

        return data
    
    except Exception as e:
        print(f"[Censys] Request failed: {e}")
        return None