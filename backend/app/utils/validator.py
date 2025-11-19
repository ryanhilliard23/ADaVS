import re
import ipaddress
from urllib.parse import urlparse

# Regex for standard domain names
DOMAIN_REGEX = re.compile(
    r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.'
    r'(?:[A-Za-z0-9-]{1,63}\.)*[A-Za-z]{2,63}$'
)

def is_valid_domain(target: str) -> bool:
    if not target or len(target) > 253:
        return False
    return bool(DOMAIN_REGEX.match(target))

def is_valid_ip_or_cidr(target: str) -> bool:
    try:
        ipaddress.ip_network(target, strict=False)
        return True
    except ValueError:
        return False

def validate_target(target: str) -> str:
    target = target.strip().lower()
    
    # Remove protocol if http:// or https://
    if target.startswith("http://") or target.startswith("https://"):
        parsed = urlparse(target)
        target = parsed.netloc.split(":")[0]
    
    if is_valid_ip_or_cidr(target):
        return target
    
    if is_valid_domain(target):
        return target
        
    raise ValueError(f"Invalid target format: {target}. Must be a valid Domain or IP/CIDR.")