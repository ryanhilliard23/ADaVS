import os
import requests

SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")

class ShodanError(Exception):
    pass

def shodan_host(ip: str):
    if not SHODAN_API_KEY:
        print("[Shodan] Key missing. Skipping.")
        return None

    url = f"https://api.shodan.io/shodan/host/{ip}"
    params = {"key": SHODAN_API_KEY}

    try:
        r = requests.get(url, params=params, timeout=10)

        if r.status_code == 404:
            return {}

        if r.status_code != 200:
            print(f"[Shodan] Error {r.status_code}: {r.text[:200]}")
            return None

        return r.json()
    except Exception as e:
        print(f"[Shodan] Request failed: {e}")
        return None


def normalize_shodan(ip: str, raw: dict):
    if not raw or "data" not in raw:
        return None

    services = []
    for item in raw["data"]:
        port = item.get("port")
        proto = item.get("transport", "tcp")
        banner = item.get("data") or item.get("banner")
        svc_name = item.get("product") or item.get("_shodan", {}).get("module")

        if type(port) != int:
            continue

        services.append({
            "port": port,
            "protocol": proto.lower(),
            "service_name": svc_name,
            "banner": banner,
        })

    hostnames_list = raw.get("hostnames", [])
    hostname = hostnames_list[0] if hostnames_list else None

    return {
        "ip_address": ip,
        "hostname": hostname,
        "os": raw.get("os"),
        "services": services,
    }