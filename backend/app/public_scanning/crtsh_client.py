import requests
from typing import List


def crtsh_subdomains(domain: str) -> List[str]:

    domain = domain.lower().strip()
    url = f"https://crt.sh/?q=%25.{domain}&output=json"

    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            print(f"[crtsh] HTTP {r.status_code}")
            return []

        data = r.json()
    except Exception as e:
        print(f"[crtsh] Error: {e}")
        return []

    names = set()

    for entry in data:
        cn_raw = entry.get("name_value", "")
        if not cn_raw:
            continue

        for name in cn_raw.split("\n"):
            name = name.strip().lower()

            if name.startswith("*."):
                name = name[2:]

            if not name.endswith(domain):
                continue

            if "." not in name:
                continue

            names.add(name)

    return sorted(names)
