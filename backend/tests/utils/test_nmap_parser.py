import pytest
from app.utils import nmap_parser


# === parse_nmap_xml() TESTS ===

def test_parse_nmap_xml_empty_or_incomplete():
    """Should raise ValueError for empty or incomplete XML."""
    with pytest.raises(ValueError, match="Incomplete or empty"):
        nmap_parser.parse_nmap_xml("")
    with pytest.raises(ValueError, match="Incomplete or empty"):
        nmap_parser.parse_nmap_xml("<nmaprun>")


def test_parse_nmap_xml_invalid_format():
    """Should raise ValueError for malformed XML with closing tag present."""
    # Contains the required </nmaprun> substring, but broken nesting (bad inner tag)
    bad_xml = "<nmaprun><host><status></nmaprun>"
    with pytest.raises(ValueError, match="Invalid XML format"):
        nmap_parser.parse_nmap_xml(bad_xml)



def test_parse_nmap_xml_valid_single_host():
    """Should correctly parse valid Nmap XML with one 'up' host."""
    xml = """<?xml version="1.0"?>
    <nmaprun>
      <host>
        <status state="up"/>
        <address addr="192.168.1.10" addrtype="ipv4"/>
        <hostnames>
          <hostname name="test-host.local"/>
        </hostnames>
        <os>
          <osmatch name="Ubuntu Linux 22.04"/>
        </os>
        <ports>
          <port protocol="tcp" portid="22">
            <state state="open"/>
            <service name="ssh" product="OpenSSH" version="8.9" extrainfo="Ubuntu"/>
          </port>
          <port protocol="tcp" portid="80">
            <state state="closed"/>
          </port>
        </ports>
      </host>
    </nmaprun>
    """

    hosts = nmap_parser.parse_nmap_xml(xml)
    assert len(hosts) == 1
    h = hosts[0]
    assert h["ip_address"] == "192.168.1.10"
    assert h["hostname"] == "test-host.local"
    assert h["os"] == "Ubuntu Linux 22.04"
    assert len(h["services"]) == 1
    s = h["services"][0]
    assert s["port"] == 22
    assert s["protocol"] == "tcp"
    assert s["service_name"] == "ssh"
    assert "OpenSSH" in s["banner"]
    assert "8.9" in s["banner"]
    assert "Ubuntu" in s["banner"]


def test_parse_nmap_xml_skips_down_hosts_and_missing_addrs():
    """Should skip hosts not 'up' and hosts missing address."""
    xml = """<nmaprun>
      <host>
        <status state="down"/>
        <address addr="10.0.0.1" addrtype="ipv4"/>
      </host>
      <host>
        <status state="up"/>
      </host>
      <host>
        <status state="up"/>
        <address addr="10.0.0.2" addrtype="ipv4"/>
        <ports>
          <port protocol="tcp" portid="80">
            <state state="open"/>
            <service name="http"/>
          </port>
        </ports>
      </host>
    </nmaprun>
    """

    hosts = nmap_parser.parse_nmap_xml(xml)
    assert len(hosts) == 1
    assert hosts[0]["ip_address"] == "10.0.0.2"


def test_parse_nmap_xml_skips_ports_not_open():
    """Should only include open ports in services list."""
    xml = """<nmaprun>
      <host>
        <status state="up"/>
        <address addr="127.0.0.1" addrtype="ipv4"/>
        <ports>
          <port protocol="tcp" portid="25"><state state="closed"/></port>
          <port protocol="udp" portid="53"><state state="open"/><service name="dns"/></port>
        </ports>
      </host>
    </nmaprun>
    """
    hosts = nmap_parser.parse_nmap_xml(xml)
    assert len(hosts) == 1
    services = hosts[0]["services"]
    assert len(services) == 1
    assert services[0]["port"] == 53
    assert services[0]["protocol"] == "udp"


def test_parse_nmap_xml_missing_optional_fields():
    """Handles missing hostname, os, service fields gracefully."""
    xml = """<nmaprun>
      <host>
        <status state="up"/>
        <address addr="172.16.0.5" addrtype="ipv4"/>
        <ports>
          <port protocol="tcp" portid="443">
            <state state="open"/>
            <service/>
          </port>
        </ports>
      </host>
    </nmaprun>
    """
    hosts = nmap_parser.parse_nmap_xml(xml)
    assert hosts[0]["hostname"] is None
    assert hosts[0]["os"] is None
    assert hosts[0]["services"][0]["service_name"] is None
    assert hosts[0]["services"][0]["banner"] is None


# === validate_parsed_data() TESTS ===

def test_validate_parsed_data_empty_or_bad_type():
    """Should return False for invalid host list inputs."""
    assert not nmap_parser.validate_parsed_data(None)
    assert not nmap_parser.validate_parsed_data([])
    assert not nmap_parser.validate_parsed_data([{"services": "notalist"}])
    assert not nmap_parser.validate_parsed_data([{"ip_address": "", "services": []}])


def test_validate_parsed_data_valid():
    """Should return True for valid parsed host data."""
    hosts = [{
        "ip_address": "192.168.0.1",
        "hostname": "router",
        "os": "Linux",
        "services": [{"port": 80, "protocol": "tcp", "service_name": "http", "banner": "Apache"}]
    }]
    assert nmap_parser.validate_parsed_data(hosts)
