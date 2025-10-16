from app.utils.nmap_parser import parse_nmap_xml, validate_parsed_data
import pytest

def test_parse_nmap_xml_happy_path():
    xml = """
    <nmaprun>
      <host>
        <status state="up"/>
        <address addr="10.50.100.50" addrtype="ipv4"/>
        <hostnames>
          <hostname name="vuln-ftp.adavs_macvlan" type="PTR"/>
        </hostnames>
        <os>
          <osmatch name="Linux 4.15 - 5.19"/>
        </os>
        <ports>
          <port protocol="tcp" portid="21">
            <state state="open"/>
            <service name="ftp" product="vsftpd" version="3.0.2"/>
          </port>
          <port protocol="udp" portid="53">
            <state state="open"/>
            <service name="dns" product="bind" version="9.16" extrainfo="(Debian)"/>
          </port>
          <!-- closed port should be ignored -->
          <port protocol="tcp" portid="22">
            <state state="closed"/>
            <service name="ssh" product="OpenSSH" version="9.0"/>
          </port>
        </ports>
      </host>
    </nmaprun>
    """
    hosts = parse_nmap_xml(xml)
    assert len(hosts) == 1
    h = hosts[0]
    assert h["ip_address"] == "10.50.100.50"
    assert h["hostname"] == "vuln-ftp.adavs_macvlan"
    assert h["os"] == "Linux 4.15 - 5.19"
    assert len(h["services"]) == 2

    svc1 = h["services"][0]
    assert svc1["port"] == 21
    assert svc1["protocol"] == "tcp"
    assert svc1["service_name"] == "ftp"
    assert svc1["banner"] == "vsftpd 3.0.2"

    svc2 = h["services"][1]
    assert svc2["port"] == 53
    assert svc2["protocol"] == "udp"
    assert svc2["service_name"] == "dns"
    # product + version + extrainfo joined
    assert svc2["banner"] == "bind 9.16 (Debian)"


def test_parse_nmap_xml_ignores_down_hosts_and_missing_ipv4():
    xml = """
    <nmaprun>
      <!-- down host should be ignored -->
      <host>
        <status state="down"/>
        <address addr="192.168.1.2" addrtype="ipv4"/>
      </host>
      <!-- no ipv4 should be ignored -->
      <host>
        <status state="up"/>
        <address addr="fe80::1" addrtype="ipv6"/>
        <ports>
          <port protocol="tcp" portid="80">
            <state state="open"/>
            <service name="http"/>
          </port>
        </ports>
      </host>
    </nmaprun>
    """
    hosts = parse_nmap_xml(xml)
    assert hosts == []


def test_parse_nmap_xml_banner_none_when_no_product_version_extrainfo():
    xml = """
    <nmaprun>
      <host>
        <status state="up"/>
        <address addr="10.0.0.2" addrtype="ipv4"/>
        <ports>
          <port protocol="tcp" portid="8080">
            <state state="open"/>
            <service name="http-proxy"/>
          </port>
        </ports>
      </host>
    </nmaprun>
    """
    hosts = parse_nmap_xml(xml)
    assert len(hosts) == 1
    svc = hosts[0]["services"][0]
    assert svc["service_name"] == "http-proxy"
    assert svc["banner"] is None  


def test_parse_nmap_xml_raises_on_invalid_xml():
    with pytest.raises(ValueError) as exc:
        parse_nmap_xml("<nmaprun><host></nmaprun>") 
    assert "Invalid XML format" in str(exc.value)


def test_validate_parsed_data_true():
    hosts = [{
        "ip_address": "10.0.0.5",
        "services": [{"port": 80, "protocol": "tcp"}]
    }]
    assert validate_parsed_data(hosts) is True


def test_validate_parsed_data_false_for_empty_hosts():
    assert validate_parsed_data([]) is False


def test_validate_parsed_data_false_for_missing_ip_or_services():
    bad1 = [{"services": []}]                     
    bad2 = [{"ip_address": "", "services": []}]   
    bad3 = [{"ip_address": "1.2.3.4"}]            
    bad4 = [{"ip_address": "1.2.3.4", "services": "notalist"}]  
    assert validate_parsed_data(bad1) is False
    assert validate_parsed_data(bad2) is False
    assert validate_parsed_data(bad3) is False
    assert validate_parsed_data(bad4) is False
