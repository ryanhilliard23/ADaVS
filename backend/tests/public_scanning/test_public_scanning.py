import pytest
from unittest.mock import MagicMock, patch
from app.public_scanning import censys_client, shodan_client, crtsh_client, dns_resolver, recon_service, merge_service

def test_censys_get_host_no_key(monkeypatch):
    monkeypatch.setattr(censys_client, "CENSYS_API_KEY", None)
    assert censys_client.censys_get_host("1.2.3.4") is None

def test_censys_get_host_success(monkeypatch):
    monkeypatch.setattr(censys_client, "CENSYS_API_KEY", "fake_key")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"result": {"ip": "1.2.3.4", "services": []}}
    
    with patch("app.public_scanning.censys_client.requests.get", return_value=mock_resp):
        result = censys_client.censys_get_host("1.2.3.4")
        assert result == {"result": {"ip": "1.2.3.4", "services": []}}

def test_censys_get_host_404(monkeypatch):
    monkeypatch.setattr(censys_client, "CENSYS_API_KEY", "fake_key")
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    
    with patch("app.public_scanning.censys_client.requests.get", return_value=mock_resp):
        assert censys_client.censys_get_host("1.2.3.4") is None

def test_censys_get_host_401(monkeypatch, capsys):
    monkeypatch.setattr(censys_client, "CENSYS_API_KEY", "fake_key")
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    
    with patch("app.public_scanning.censys_client.requests.get", return_value=mock_resp):
        assert censys_client.censys_get_host("1.2.3.4") is None

def test_censys_get_host_error(monkeypatch):
    monkeypatch.setattr(censys_client, "CENSYS_API_KEY", "fake_key")
    with patch("app.public_scanning.censys_client.requests.get", side_effect=Exception("boom")):
        assert censys_client.censys_get_host("1.2.3.4") is None

def test_shodan_host_no_key(monkeypatch):
    monkeypatch.setattr(shodan_client, "SHODAN_API_KEY", None)
    assert shodan_client.shodan_host("1.2.3.4") is None

def test_shodan_host_success(monkeypatch):
    monkeypatch.setattr(shodan_client, "SHODAN_API_KEY", "fake_key")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"ip_str": "1.2.3.4", "ports": [80]}
    
    with patch("app.public_scanning.shodan_client.requests.get", return_value=mock_resp):
        result = shodan_client.shodan_host("1.2.3.4")
        assert result["ip_str"] == "1.2.3.4"

def test_shodan_host_404(monkeypatch):
    monkeypatch.setattr(shodan_client, "SHODAN_API_KEY", "fake_key")
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    
    with patch("app.public_scanning.shodan_client.requests.get", return_value=mock_resp):
        assert shodan_client.shodan_host("1.2.3.4") == {}

def test_shodan_host_error(monkeypatch):
    monkeypatch.setattr(shodan_client, "SHODAN_API_KEY", "fake_key")
    with patch("app.public_scanning.shodan_client.requests.get", side_effect=Exception("boom")):
        assert shodan_client.shodan_host("1.2.3.4") is None

def test_normalize_shodan():
    raw = {
        "os": "Linux",
        "hostnames": ["example.com"],
        "data": [
            {"port": 80, "transport": "tcp", "product": "nginx", "data": "banner"},
            {"port": "invalid"}, 
        ]
    }
    res = shodan_client.normalize_shodan("1.1.1.1", raw)
    assert res["ip_address"] == "1.1.1.1"
    assert res["hostname"] == "example.com"
    assert len(res["services"]) == 1
    assert res["services"][0]["port"] == 80

def test_crtsh_subdomains_success():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        {"name_value": "example.com"},
        {"name_value": "*.example.com"},
        {"name_value": "sub.example.com\nanother.example.com"}
    ]
    
    with patch("app.public_scanning.crtsh_client.requests.get", return_value=mock_resp):
        results = crtsh_client.crtsh_subdomains("example.com")
        assert "sub.example.com" in results
        assert "example.com" in results
        assert "*.example.com" not in results 

def test_crtsh_subdomains_failure():
    with patch("app.public_scanning.crtsh_client.requests.get", side_effect=Exception("fail")):
        assert crtsh_client.crtsh_subdomains("example.com") == []

def test_resolve_hostnames():
    mock_answer = MagicMock()
    mock_answer.to_text.return_value = "1.2.3.4"
    
    with patch("app.public_scanning.dns_resolver.dns.resolver.resolve", return_value=[mock_answer]):
        res = dns_resolver.resolve_hostnames(["example.com"])
        assert "1.2.3.4" in res
        assert "example.com" in res["1.2.3.4"]

def test_resolve_hostnames_error():
    with patch("app.public_scanning.dns_resolver.dns.resolver.resolve", side_effect=Exception("nxdomain")):
        res = dns_resolver.resolve_hostnames(["bad.com"])
        assert res == {}

def test_merge_asset():
    ip = "1.2.3.4"
    hostnames = ["test.com"]
    censys = {
        "result": {
            "services": [{"port": 80, "transport_protocol": "TCP", "service_name": "http"}],
            "operating_system": {"product": "Ubuntu"}
        }
    }
    shodan = {
        "ip_address": ip,
        "hostname": "shodan.com",
        "os": "Debian",
        "services": [{"port": 443, "protocol": "tcp", "banner": "ssl"}]
    }
    
    result = merge_service.merge_asset(ip, hostnames, censys, shodan)
    assert result["ip_address"] == ip
    assert len(result["services"]) == 2
    
    assert result["hostname"] == "shodan.com" 
    assert result["os"] == "Debian" 

def test_recon_service_flow(monkeypatch):
    monkeypatch.setattr(recon_service, "enumerate_subdomains", lambda d: ["sub.test.com"])
    monkeypatch.setattr(recon_service, "resolve_hostnames", lambda h: {"1.2.3.4": {"sub.test.com"}})
    monkeypatch.setattr(recon_service, "censys_get_host", lambda ip: None)
    monkeypatch.setattr(recon_service, "shodan_host", lambda ip: {})
    monkeypatch.setattr(recon_service, "normalize_shodan", lambda ip, raw: None)
    
    def fake_merge(ip, names, c, s):
        return {
            "ip_address": ip, 
            "services": [{"port": 80}] 
        }
    monkeypatch.setattr(recon_service, "merge_asset", fake_merge)

    assets = recon_service.discover_domain_assets("test.com")
    assert len(assets) == 1
    assert assets[0]["ip_address"] == "1.2.3.4"