"""Existing regression tests: these must pass before AND after the patch."""
from target_sample import app, search_users


def test_finds_existing_user():
    result = search_users("alice")
    assert len(result) == 1 and result[0]["username"] == "alice"


def test_unknown_user_returns_empty():
    assert search_users("nobody") == []


def test_search_endpoint():
    client = app.test_client()
    response = client.get("/search?name=bob")
    assert response.status_code == 200
    assert response.get_json()[0]["username"] == "bob"