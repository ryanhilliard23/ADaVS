import xml.etree.ElementTree as ET
from typing import List, Dict, Optional

def parse_nmap_xml(xml_string: str) -> List[Dict]:
    """
    Parse nmap XML output and return a list of discovered hosts with their services.
    
    Returns:
        List of dicts with structure:
        [{
            'ip_address': '10.50.100.50',
            'hostname': 'vuln-ftp.adavs_macvlan',
            'os': 'Linux 4.15 - 5.19',
            'services': [
                {
                    'port': 21,
                    'protocol': 'tcp',
                    'service_name': 'ftp',
                    'banner': 'vsftpd 3.0.2'
                }
            ]
        }]
    """
    try:
        root = ET.fromstring(xml_string)
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML format: {str(e)}")
    
    hosts = []
    
    for host in root.findall('host'):
        status = host.find('status')
        if status is None or status.get('state') != 'up':
            continue
        
        addr_elem = host.find("address[@addrtype='ipv4']")
        if addr_elem is None:
            continue
        ip_address = addr_elem.get('addr')
        
        hostname = None
        hostname_elem = host.find("hostnames/hostname[@type='PTR']")
        if hostname_elem is not None:
            hostname = hostname_elem.get('name')
        
        os_info = None
        osmatch = host.find('os/osmatch')
        if osmatch is not None:
            os_info = osmatch.get('name')
        
        services = []
        ports = host.find('ports')
        if ports is not None:
            for port in ports.findall('port'):
                state = port.find('state')
                if state is None or state.get('state') != 'open':
                    continue
                
                port_id = port.get('portid')
                protocol = port.get('protocol', 'tcp')
                
                service = port.find('service')
                service_name = None
                banner = None
                
                if service is not None:
                    service_name = service.get('name')
                    product = service.get('product', '')
                    version = service.get('version', '')
                    extrainfo = service.get('extrainfo', '')
                    
                    banner_parts = [p for p in [product, version, extrainfo] if p]
                    banner = ' '.join(banner_parts) if banner_parts else None
                
                services.append({
                    'port': int(port_id),
                    'protocol': protocol,
                    'service_name': service_name,
                    'banner': banner
                })
        
        if services:
            hosts.append({
                'ip_address': ip_address,
                'hostname': hostname,
                'os': os_info,
                'services': services
            })
    
    return hosts


def validate_parsed_data(hosts: List[Dict]) -> bool:
    """Validate that parsed data has required fields."""
    if not hosts:
        return False
    
    for host in hosts:
        if 'ip_address' not in host or not host['ip_address']:
            return False
        if 'services' not in host or not isinstance(host['services'], list):
            return False
    
    return True