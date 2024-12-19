import pytest

from .test_base import client


@pytest.mark.dependency()
def test_api():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.text == 'Hello from Joban API'
