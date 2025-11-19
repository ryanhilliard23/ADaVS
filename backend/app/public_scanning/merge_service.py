from typing import Dict, Any, Iterable, Tuple, Optional


def _normalize_censys(ip: str, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:

    if not raw:
        return None

    result = raw.get("result", raw)

    services_out = []
    for svc in result.get("services", []):
        port = svc.get("port")
        if not isinstance(port, int):
            continue

        proto = (svc.get("transport_protocol") or svc.get("transport") or "tcp").lower()
        svc_name = svc.get("service_name")
        banner = svc.get("banner")

        services_out.append(
            {
                "port": port,
                "protocol": proto,
                "service_name": svc_name,
                "banner": banner,
            }
        )

    os_name = None
    os_data = result.get("operating_system") or result.get("os")
    if isinstance(os_data, dict):
        os_name = os_data.get("name") or os_data.get("product")
    elif isinstance(os_data, str):
        os_name = os_data

    return {
        "ip_address": ip,
        "hostname": None,  
        "os": os_name,
        "services": services_out,
    }


def _normalize_shodan(ip: str, shodan_normalized: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not shodan_normalized:
        return None
    return shodan_normalized


def _merge_services(
    base_services: Iterable[Dict[str, Any]],
    extra_services: Iterable[Dict[str, Any]],
) -> list[Dict[str, Any]]:

    out = list(base_services)
    seen: set[Tuple[int, str]] = {(s["port"], s["protocol"]) for s in out if "port" in s and "protocol" in s}

    for svc in extra_services:
        port = svc.get("port")
        proto = svc.get("protocol", "tcp").lower()
        if not isinstance(port, int):
            continue
        key = (port, proto)
        if key in seen:
            continue
        seen.add(key)
        out.append(
            {
                "port": port,
                "protocol": proto,
                "service_name": svc.get("service_name"),
                "banner": svc.get("banner"),
            }
        )

    return out


def merge_asset(
    ip: str,
    hostnames: Iterable[str],
    censys_raw: Dict[str, Any] | None,
    shodan_normalized: Dict[str, Any] | None,
) -> Dict[str, Any]:
    
    censys_norm = _normalize_censys(ip, censys_raw) if censys_raw else None
    shodan_norm = _normalize_shodan(ip, shodan_normalized) if shodan_normalized else None

    asset = {
        "ip_address": ip,
        "hostname": None,
        "os": None,
        "services": [],
    }

    dns_hostname = next(iter(hostnames), None)

    if censys_norm:
        asset["os"] = censys_norm.get("os") or asset["os"]
        asset["services"] = _merge_services(asset["services"], censys_norm.get("services", []))

    if shodan_norm:
        asset["hostname"] = shodan_norm.get("hostname") or asset["hostname"]
        asset["os"] = shodan_norm.get("os") or asset["os"]
        asset["services"] = _merge_services(asset["services"], shodan_norm.get("services", []))

    if not asset["hostname"]:
        asset["hostname"] = dns_hostname

    return asset
