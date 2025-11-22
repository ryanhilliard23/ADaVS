# backend/tests/utils/test_validator.py
import pytest
from app.utils.validator import validate_target

def test_validate_target_valid_ip():
    """Should return IP as-is for valid inputs."""
    assert validate_target("192.168.1.1") == "192.168.1.1"
    assert validate_target("  10.0.0.5  ") == "10.0.0.5"

def test_validate_target_valid_cidr():
    """Should allow CIDR notation."""
    assert validate_target("10.50.100.0/24") == "10.50.100.0/24"

def test_validate_target_valid_domain():
    """Should allow valid domains and strip protocols."""
    assert validate_target("example.com") == "example.com"
    assert validate_target("https://www.google.com") == "www.google.com"
    assert validate_target("http://sub.site.org:8080") == "sub.site.org"

def test_validate_target_invalid_inputs():
    """Should raise ValueError for dangerous or invalid inputs."""
    invalid_inputs = [
        "; ls -la",          # Command injection attempt
        "127.0.0.1 && cat",  # Chaining attempt
        "not_a_domain",      # Gibberish
        "192.168.1.256",     # Invalid IP
        "",                  # Empty
    ]
    for inp in invalid_inputs:
        with pytest.raises(ValueError):
            validate_target(inp)