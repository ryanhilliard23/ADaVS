from .crtsh_client import crtsh_subdomains

COMMON_LABELS = [
    "www",
    "mail",
    "smtp",
    "api",
    "vpn",
    "portal",
    "login",
    "apps",
]


def enumerate_subdomains(domain: str) -> list[str]:
    domain = domain.lower().strip()
    if not domain:
        return []

    hosts = set()

    hosts.add(domain)

    try:
        for name in crtsh_subdomains(domain):
            hosts.add(name.lower().strip())
    except Exception as e:
        print(f"[subdomain_enum] crt.sh lookup failed: {e}")

    for label in COMMON_LABELS:
        hosts.add(f"{label}.{domain}")

    return sorted(hosts)
