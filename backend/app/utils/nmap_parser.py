import xml.etree.ElementTree as ET
from typing import List, Dict

def parse_nmap_xml(xml_string: str) -> List[Dict]:
    if not xml_string or "</nmaprun>" not in xml_string:
        raise ValueError("Incomplete or empty Nmap XML.")
    try:
        root = ET.fromstring(xml_string)

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML format: {e}")
    
    
    hosts: List[Dict] = []

    for host in root.findall("host"):
        status = host.find("status")
         
        print ("status")
        if status is None or status.get("state") != "up":
            continue

        addr_elem = host.find("address[@addrtype='ipv4']")
        print(addr_elem)
         
        if addr_elem is None:
            addr_elem = host.find("address")
        if addr_elem is None:
            continue

        ip_address = addr_elem.get("addr")
        print(ip_address)
        if not ip_address:
            continue

        hostname = None
        hn = host.find("hostnames/hostname")
        if hn is not None:
            hostname = hn.get("name") or None
        print(hostname)

        os_name = None
        osmatch = host.find("os/osmatch")
        if osmatch is not None:
            os_name = osmatch.get("name") or None
        print(os_name)

        services = []
        ports = host.find("ports")
        print(ports)
        if ports is not None:
            for port in ports.findall("port"):
                 
                print(port)
                state = port.find("state")
                print(state)
                if state is None or state.get("state") != "open":
                    continue

                port_id = port.get("portid")
                proto = (port.get("protocol") or "tcp").lower()

                service_name = None
                banner = None
                service = port.find("service")
                if service is not None:
                    service_name = service.get("name") or None
                    product = service.get("product") or ""
                    version = service.get("version") or ""
                    extrainfo = service.get("extrainfo") or ""
                    parts = [p for p in (product, version, extrainfo) if p]
                    banner = " ".join(parts) if parts else None
                print(service_name)
                print(product)
                try:
                    port_int = int(port_id)
                except (TypeError, ValueError):
                    continue

                services.append({
                    "port": port_int,
                    "protocol": proto,
                    "service_name": service_name,
                    "banner": banner
                })

        if services:
            hosts.append({
                "ip_address": ip_address,
                "hostname": hostname,
                "os": os_name,
                "services": services
            })

    return hosts


def validate_parsed_data(hosts: List[Dict]) -> bool:
    if not hosts:
        return False
    for h in hosts:
        if not h.get("ip_address"):
            return False
        if not isinstance(h.get("services"), list):
            return False
    return True
