from .test_base import client

import pytest

def pytest_configure():
    pytest.token = ""


@pytest.mark.dependency()
def test_board_new():
    login_resp = client.post("/auth/login",
                             json={
                                 "login": "ross",
                                 "password": "1234"
                             })
    
    resp = client.post("/boards/new",
        json={
            "title": "test board",
            "columns": [
                {
                    "title": "test column",
                    "orderNumber": 1
                }
            ]
        },
        cookies={"DxpAccessToken": login_resp.cookies.get("DxpAccessToken")}
    )
    pytest.token = login_resp.cookies.get("DxpAccessToken")
    assert resp.status_code == 200
    assert resp.json() == {
        "id": 1,
        "title": "test board"
    }


@pytest.mark.dependency(depends=["test_board_new"])
def test_token_check():
    resp = client.get("/boards/1")
    assert resp.status_code == 401


@pytest.mark.dependency(depends=["test_board_new"])
def test_board_list_get():
    resp = client.get("/boards",
        cookies={"DxpAccessToken": pytest.token}
    )
    assert resp.status_code == 200
    assert resp.json() == [
        {
            "id": 1,
            "title": "test board"
        }
    ]
    resp = client.post("/boards/new",
        json={
            "title": "test board 2",
            "columns": [
                {
                    "title": "test column",
                    "orderNumber": 1
                }
            ]
        },
        cookies={"DxpAccessToken": pytest.token}
    )
    resp = client.get("/boards",
        cookies={"DxpAccessToken": pytest.token}
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.dependency(depends=["test_board_new"])
def test_board_get():
    resp = client.get("/boards/1",
        cookies={"DxpAccessToken": pytest.token}
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "id": 1,
        "title": "test board",
        "columns": [
            {
                "title": "test column",
                'boardId': 1,
                'id': 1,
                'orderNumber': 1,
                'tasks': []
            }
        ]
    }
    resp = client.get("/boards/3",
        cookies={"DxpAccessToken": pytest.token}
    )
    assert resp.status_code == 404


@pytest.mark.dependency()
def test_board_delete():
    resp = client.delete("/boards/2",
        cookies={"DxpAccessToken": pytest.token}
    )
    assert resp.status_code == 200
    resp = client.get("/boards",
        cookies={"DxpAccessToken": pytest.token}
    )
    assert len(resp.json()) == 1

    resp = client.delete("/boards/3",
        cookies={"DxpAccessToken": pytest.token}
    )
    assert resp.status_code == 404


@pytest.mark.dependency()
def test_board_put():
    resp = client.put("/boards/1",
        json={
            "id": 1,
            "title": "test board changed",
            "columns": [
                {
                    "title": "test column changed",
                    'boardId': 1,
                    'id': 1,
                    'orderNumber': 1,
                    'tasks': []
                }
            ]
        },
        cookies={"DxpAccessToken": pytest.token}
    )
    assert resp.status_code == 200
    
    resp = client.get("/boards/1",
        cookies={"DxpAccessToken": pytest.token}
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "id": 1,
        "title": "test board changed",
        "columns": [
            {
                "title": "test column changed",
                'boardId': 1,
                'id': 1,
                'orderNumber': 1,
                'tasks': []
            }
        ]
    }


