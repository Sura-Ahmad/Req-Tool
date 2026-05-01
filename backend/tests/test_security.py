"""Unit tests for app/core/security.py — no database needed."""
import pytest
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, verify_token


def test_hash_password_produces_unique_hashes():
    pwd = "TestPass123"
    h1 = hash_password(pwd)
    h2 = hash_password(pwd)
    assert h1 != h2  # bcrypt embeds a random salt


def test_verify_password_correct():
    pwd = "SecurePass99"
    assert verify_password(pwd, hash_password(pwd)) is True


def test_verify_password_wrong():
    assert verify_password("wrong", hash_password("correct")) is False


def test_verify_password_empty_against_hash():
    assert verify_password("", hash_password("notempty")) is False


def test_create_access_token_returns_string():
    token = create_access_token({"sub": "user-uuid-123"})
    assert isinstance(token, str)
    assert len(token) > 20


def test_create_refresh_token_returns_string():
    token = create_refresh_token({"sub": "user-uuid-456"})
    assert isinstance(token, str)
    assert len(token) > 20


def test_access_and_refresh_tokens_are_different():
    payload = {"sub": "same-user"}
    access = create_access_token(payload)
    refresh = create_refresh_token(payload)
    assert access != refresh


def test_verify_token_valid_access():
    token = create_access_token({"sub": "abc-123"})
    payload = verify_token(token)
    assert payload is not None
    assert payload["sub"] == "abc-123"


def test_verify_token_valid_refresh():
    token = create_refresh_token({"sub": "xyz-789"})
    payload = verify_token(token)
    assert payload is not None
    assert payload["sub"] == "xyz-789"


def test_verify_token_invalid_string():
    assert verify_token("not.a.real.token") is None


def test_verify_token_tampered():
    token = create_access_token({"sub": "user-1"})
    tampered = token[:-8] + "XXXXXXXX"
    assert verify_token(tampered) is None


def test_verify_token_empty_string():
    assert verify_token("") is None
