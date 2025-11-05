import xml.etree.ElementTree as ET


def parse_nmap_xml(xml_str: str):
    """
    Parse Nmap XML output into structured host data.

    Returns:
        list[dict]: Each dict has ip_address, hostname, os, services (list of dicts)
    """
    hosts = []

    try:
        root = ET.fromstring(xml_str)
    except ET.ParseError as exc:
        raise ValueError(f"Invalid XML format: {exc}")

    for host_elem in root.findall("host"):
        # Skip hosts that are not 'up'
        status = host_elem.find("status")
        if status is not None and status.get("state") != "up":
            continue

        # Find IPv4 address (ignore IPv6)
        ip_addr = None
        for addr_elem in host_elem.findall("address"):
            if addr_elem.get("addrtype") == "ipv4":
                ip_addr = addr_elem.get("addr")
                break
        if not ip_addr:  # skip missing ipv4
            continue

        # Hostname (optional)
        hostname = None
        hostnames_elem = host_elem.find("hostnames")
        if hostnames_elem is not None:
            hn_elem = hostnames_elem.find("hostname")
            if hn_elem is not None:
                hostname = hn_elem.get("name")

        # OS fingerprint (optional)
        os_match = None
        os_elem = host_elem.find("os")
        if os_elem is not None:
            match = os_elem.find("osmatch")
            if match is not None:
                os_match = match.get("name")

        # Parse services
        services = []
        ports_elem = host_elem.find("ports")
        if ports_elem is not None:
            for port_elem in ports_elem.findall("port"):
                state_elem = port_elem.find("state")
                if state_elem is None or state_elem.get("state") != "open":
                    continue

                proto = port_elem.get("protocol")
                port_id = int(port_elem.get("portid"))
                service_elem = port_elem.find("service")
                service_name = service_elem.get("name") if service_elem is not None else None

                # build banner from product/version/extrainfo
                banner = None
                if service_elem is not None:
                    parts = []
                    for key in ("product", "version", "extrainfo"):
                        val = service_elem.get(key)
                        if val:
                            parts.append(val)
                    banner = " ".join(parts) if parts else None

                services.append({
                    "port": port_id,
                    "protocol": proto,
                    "service_name": service_name,
                    "banner": banner,
                })

        hosts.append({
            "ip_address": ip_addr,
            "hostname": hostname,
            "os": os_match,
            "services": services,
        })

    return hosts


def validate_parsed_data(hosts):
    """
    Validate the parsed host/service data structure.
    Must contain at least one host, each with a valid IPv4 and nonempty services list.
    """
    if not isinstance(hosts, list) or not hosts:
        return False

    for h in hosts:
        ip = h.get("ip_address")
        services = h.get("services")
        if not ip or not isinstance(services, list) or len(services) == 0:
            return False

    return True
