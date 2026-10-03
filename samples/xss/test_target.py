"""Existing regression tests: these must pass before AND after the patch."""
from target_sample import app, render_greeting


def test_greets_by_name():
    assert render_greeting("Alice") == "<h1>Hello, Alice!</h1>"


def test_greet_endpoint():
    client = app.test_client()
    response = client.get("/greet?name=Bob")
    assert response.status_code == 200
    assert "Hello, Bob" in response.data.decode()


def test_default_guest():
    assert "guest" in app.test_client().get("/greet").data.decode()