from typing import Dict, List
from .subdomain_enum import enumerate_subdomains
from .dns_resolver import resolve_hostnames
from .censys_client import censys_get_host
from .shodan_client import shodan_host, normalize_shodan
from .merge_service import merge_asset


def discover_domain_assets(domain: str) -> List[Dict]:

    domain = domain.lower().strip()
    if not domain:
        return []

    print(f"[recon] Starting passive discovery for domain: {domain}")

    hostnames = enumerate_subdomains(domain)
    print(f"[recon] Hostnames to investigate: {len(hostnames)}")

    if not hostnames:
        return []

    ip_to_hosts = resolve_hostnames(hostnames)
    print(f"[recon] Resolved to {len(ip_to_hosts)} unique IP(s)")

    assets: List[Dict] = []

    for ip, names in ip_to_hosts.items():
        print(f"[recon] Enriching {ip} ({', '.join(names)})")

        censys_raw = None
        shodan_norm = None

        try:
            censys_raw = censys_get_host(ip)
        except Exception as e:
            print(f"[recon] Censys lookup failed for {ip}: {e}")

        try:
            shodan_raw = shodan_host(ip)
            if shodan_raw:
                shodan_norm = normalize_shodan(ip, shodan_raw)
        except Exception as e:
            print(f"[recon] Shodan lookup failed for {ip}: {e}")

        asset = merge_asset(ip, names, censys_raw, shodan_norm)

        if asset["services"]:
            assets.append(asset)

    print(f"[recon] Discovery finished. Assets with services: {len(assets)}")
    return assets
