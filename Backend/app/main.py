from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from contextlib import asynccontextmanager
from app.db import create_db_and_tables
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth
from app.routers import boards
from app.routers import columns
from app.routers import tasks

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(auth.router)
app.include_router(boards.router)
app.include_router(columns.router)
app.include_router(tasks.router)


# origins = [
#     "http://localhost:5173",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=PlainTextResponse)
async def root():
    return "Hello from Joban API"