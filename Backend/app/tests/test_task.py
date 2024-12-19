from .test_base import client

import pytest

@pytest.mark.dependency()
def test_task_new():
    resp = client.post("/tasks/new",
        json={
            "title": "test task",
            "description": '''
This is a multiline description of a *task*
''',
            "columnId": 1
        },
        cookies={"DxpAccessToken": pytest.token}
    )
    assert resp.status_code == 200


@pytest.mark.dependency(depends=["test_task_new"])
def test_task_get():
    resp = client.get("/tasks/1",
        cookies={"DxpAccessToken": pytest.token}
    )
    assert resp.status_code == 200
    assert resp.json() == {
            "id": 1,
            "col_id": 1,
            "ord_num": 0,
            "title": "test task",
            "body": '''
This is a multiline description of a *task*
'''
        }
    resp = client.get("/tasks/2",
        cookies={"DxpAccessToken": pytest.token}
    )
    assert resp.status_code == 404


@pytest.mark.dependency(depends=["test_task_new"])
def test_task_in_board():
    resp = client.post("/tasks/new",
        json={
            "title": "test task 2",
            "description": "Hello World",
            "columnId": 1
        },
        cookies={"DxpAccessToken": pytest.token}
    )
    resp = client.get("/boards/1",
        cookies={"DxpAccessToken": pytest.token}
    )
    assert len(resp.json().get("columns")[0].get("tasks")) == 2
    assert resp.json().get("columns")[0].get("tasks")[1].get("title") == "test task 2"


@pytest.mark.dependency(depends=["test_task_new"])
def test_task_delete():
    resp = client.delete("/tasks/2",
                         cookies={"DxpAccessToken": pytest.token})
    assert resp.status_code == 200
    resp = client.get("/boards/1",
        cookies={"DxpAccessToken": pytest.token}
    )
    assert len(resp.json().get("columns")[0].get("tasks")) == 1

    resp = client.delete("/tasks/3",
                         cookies={"DxpAccessToken": pytest.token})
    assert resp.status_code == 404


@pytest.mark.dependency(depends=["test_task_new"])
def test_task_put():
    resp = client.put("/tasks/1",
                        json={
                            "title": "New Title",
                            "description": "New Description",
                            "columnId": 1
                        },
                        cookies={"DxpAccessToken": pytest.token})
    assert resp.status_code == 200
    
    resp = client.get("/tasks/1",
        cookies={"DxpAccessToken": pytest.token}
    )
    assert resp.json() == {
            "id": 1,
            "col_id": 1,
            "ord_num": 0,
            "title": "New Title",
            "body": "New Description"
        }
    
    resp = client.put("/tasks/3",
                        json={
                            "title": "New Title",
                            "description": "New Description",
                            "columnId": 1
                        },
                        cookies={"DxpAccessToken": pytest.token})
    assert resp.status_code == 404
    
    