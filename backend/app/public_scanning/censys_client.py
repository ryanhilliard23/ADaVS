import os
import requests

CENSYS_API_KEY = os.getenv("CENSYS_API_KEY")

BASE_URL = "https://search.censys.io/api/v2"


class CensysError(Exception):
    pass


def censys_get_host(ip: str):
    if not CENSYS_API_KEY:
        raise CensysError("CENSYS_API_KEY not set in environment")

    url = f"{BASE_URL}/hosts/{ip}"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {CENSYS_API_KEY}",
    }

    r = requests.get(url, headers=headers)

    if r.status_code == 404:
        return None

    if r.status_code != 200:
        raise CensysError(f"Censys error {r.status_code}: {r.text[:200]}")

    data = r.json()

    if "result" not in data:
        return None

    return data
