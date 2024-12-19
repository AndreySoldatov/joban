import hashlib
import pytest

from .test_base import client

@pytest.mark.dependency()
def test_reg():
    resp = client.post("/auth/register",
                       json={
                           "first_name": "robot",
                           "last_name": "bobot",
                           "login": "ross",
                           "password": "1234"
                       })
    assert resp.status_code == 201

    hasher = hashlib.sha256()
    hasher.update(("1234" + resp.json().get("salt")).encode())

    assert resp.json().get("password_hash") == hasher.hexdigest()

    resp = client.post("/auth/register",
                       json={
                           "first_name": "robot",
                           "last_name": "bobot",
                           "login": "ross",
                           "password": "1234"
                       })
    assert resp.status_code == 409

@pytest.mark.dependency(depends=["test_reg"])
def test_login():
    login_wrong_user = client.post("/auth/login",
                                   json={
                                       "login": "lol",
                                       "password": "1234"
                                   })
    assert login_wrong_user.status_code == 404

    login_wrong_password = client.post("/auth/login",
                                       json={
                                           "login": "ross",
                                           "password": "4321"
                                       })
    assert login_wrong_password.status_code == 401

    login_resp = client.post("/auth/login",
                             json={
                                 "login": "ross",
                                 "password": "1234"
                             })
    assert login_resp.status_code == 200
    assert len(login_resp.cookies.get("DxpAccessToken")) == 64
    assert login_resp.json() == {"displayName": "robot bobot"}


@pytest.mark.dependency(depends=["test_login"])
def test_whoami():
    login_resp = client.post("/auth/login",
                             json={
                                 "login": "ross",
                                 "password": "1234"
                             })

    whoami_resp = client.get(
        "/auth/whoami", cookies={"DxpAccessToken": login_resp.cookies.get("DxpAccessToken")})
    assert whoami_resp.json() == {"displayName": "robot bobot"}

    whoami_resp = client.get("/auth/whoami")
    assert whoami_resp.status_code == 401


@pytest.mark.dependency(depends=["test_login"])
def test_logout():
    login_resp = client.post("/auth/login",
                             json={
                                 "login": "ross",
                                 "password": "1234"
                             })

    logout_resp = client.post(
        "/auth/logout", cookies={"DxpAccessToken": login_resp.cookies.get("DxpAccessToken")})
    assert logout_resp.text == '"logout"'

