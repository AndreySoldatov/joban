from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from ..main import app
from ..db import get_session

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