import pytest
import json
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

import app.services.user_services as us

us.pwd_context.hash = lambda pwd: f"fake-hash-{pwd}"
us.pwd_context.verify = lambda plain, hashed: hashed == f"fake-hash-{plain}"

@pytest.fixture
def fake_user_obj():
    class DummyUser:
        id = 1
        email = "test@example.com"
        hashed_password = us.get_password_hash("secret")
    return DummyUser()


def test_get_password_hash_and_verify():
    pwd = "mypassword"
    hashed = us.get_password_hash(pwd)
    assert hashed != pwd
    assert us.verify_password(pwd, hashed)
    assert not us.verify_password("wrong", hashed)


def test_get_user_by_email(monkeypatch, fake_user_obj):
    mock_db = Mock()
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = fake_user_obj

    out = us.get_user_by_email(mock_db, "test@example.com")
    assert out.email == "test@example.com"
    mock_db.query.assert_called_once()


def test_create_user(monkeypatch):
    mock_db = Mock()
    mock_user_model = Mock()
    monkeypatch.setattr(us, "user_model", mock_user_model)

    fake_user = us.UserCreate(email="new@x.com", password="pwd")
    mock_user_model.User.return_value = Mock(email=fake_user.email, hashed_password="hash")

    result = us.create_user(mock_db, fake_user)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
    assert result.email == fake_user.email


def test_authenticate_user_success(monkeypatch, fake_user_obj):
    monkeypatch.setattr(us, "get_user_by_email", lambda db, email: fake_user_obj)
    monkeypatch.setattr(us, "verify_password", lambda plain, hashed: True)
    out = us.authenticate_user(Mock(), "t@x.com", "secret")
    assert out == fake_user_obj


def test_authenticate_user_failure(monkeypatch, fake_user_obj):
    monkeypatch.setattr(us, "get_user_by_email", lambda db, email: None)
    assert us.authenticate_user(Mock(), "t@x.com", "secret") is None

    monkeypatch.setattr(us, "get_user_by_email", lambda db, email: fake_user_obj)
    monkeypatch.setattr(us, "verify_password", lambda plain, hashed: False)
    assert us.authenticate_user(Mock(), "t@x.com", "wrong") is None


def test_create_access_token_and_decode(monkeypatch, fake_user_obj):
    fake_payload = {
        "sub": fake_user_obj.email,
        "user_id": fake_user_obj.id,
        "exp": (datetime.utcnow() + timedelta(minutes=30)).isoformat()
    }

    # mock pyseto.encode → return json bytes
    monkeypatch.setattr(us.pyseto, "encode", lambda key, payload, footer: json.dumps(payload).encode())
    token = us.create_access_token(fake_user_obj)
    assert fake_user_obj.email in token


def test_get_current_user_valid(monkeypatch, fake_user_obj):
    payload = {"sub": fake_user_obj.email, "user_id": fake_user_obj.id}
    fake_decoded = Mock(payload=json.dumps(payload).encode())

    monkeypatch.setattr(us.pyseto, "decode", lambda key, token: fake_decoded)
    out = us.get_current_user("sometoken")
    assert out == {"user_id": 1, "email": "test@example.com"}


def test_get_current_user_invalid_payload(monkeypatch):
    bad_payload = json.dumps({"foo": "bar"}).encode()
    fake_decoded = Mock(payload=bad_payload)
    monkeypatch.setattr(us.pyseto, "decode", lambda k, t: fake_decoded)

    from fastapi import HTTPException
    with pytest.raises(HTTPException) as e:
        us.get_current_user("token")
    assert e.value.status_code == 401


def test_get_current_user_decode_failure(monkeypatch):
    monkeypatch.setattr(us.pyseto, "decode", lambda *a, **k: (_ for _ in ()).throw(Exception("bad token")))
    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        us.get_current_user("token")
