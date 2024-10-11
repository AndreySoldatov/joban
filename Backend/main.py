from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
from db import create_db_and_tables, User, SessionDep
from sqlmodel import select
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=PlainTextResponse)
async def root():
    return "To access api use /api/"

@app.get("/api")
async def api():
    return "Hello API!"

@app.post("/api/auth/register", status_code=201)
async def login(user: User, session: SessionDep):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.post("/api/auth/login", status_code=200)
async def login(user: User, session: SessionDep):
    query = select(User).where(User.login == user.login)
    db_user = session.exec(query).first()
    if not db_user:
        return PlainTextResponse("User not found", status_code=401)
    if user.password != db_user.password:
        return PlainTextResponse("Wrong password", status_code=401)
    return db_user