from typing import Dict, Set, List
import dns.resolver


def resolve_hostnames(hostnames: List[str]) -> Dict[str, Set[str]]:

    ip_to_hosts: Dict[str, Set[str]] = {}

    for name in hostnames:
        try:
            answers = dns.resolver.resolve(name, "A")
        except Exception:
            continue

        for r in answers:
            ip = r.to_text()
            if not ip:
                continue
            if ip not in ip_to_hosts:
                ip_to_hosts[ip] = set()
            ip_to_hosts[ip].add(name)

    return ip_to_hosts
