from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from ..main import app
from ..db import get_session

import hashlib

engine = engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SQLModel.metadata.create_all(engine)


def get_session_override():
    with Session(engine) as session:
        return session


app.dependency_overrides[get_session] = get_session_override
client = TestClient(app)


def test_reg():
    resp = client.post("/auth/register",
                       json={
                           "first_name": "Andrey",
                           "last_name": "Soldatov",
                           "login": "ross",
                           "password": "qwer4132"
                       })
    assert resp.status_code == 201

    hasher = hashlib.sha256()
    hasher.update(("qwer4132" + resp.json().get("salt")).encode())

    assert resp.json().get("password_hash") == hasher.hexdigest()
