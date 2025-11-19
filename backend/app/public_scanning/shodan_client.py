import os
import requests

SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")


class ShodanError(Exception):
    pass


def shodan_host(ip: str):
    if not SHODAN_API_KEY:
        raise ShodanError("SHODAN_API_KEY not set")

    url = f"https://api.shodan.io/shodan/host/{ip}"
    params = {"key": SHODAN_API_KEY}

    r = requests.get(url, params=params)

    if r.status_code == 404:
        return {}

    if r.status_code != 200:
        raise ShodanError(f"Shodan error {r.status_code}: {r.text[:200]}")

    return r.json()


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

    return {
        "ip_address": ip,
        "hostname": raw.get("hostnames", [None])[0],
        "os": raw.get("os"),
        "services": services,
    }
