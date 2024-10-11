from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

app = FastAPI()

@app.get("/", response_class=PlainTextResponse)
async def root():
    return "To access api use /api/"

@app.get("/api/")
async def api():
    return "Hello API!"

class LoginCredentials(BaseModel):
    username: str
    password: str

@app.post("/api/auth/login", status_code=200)
async def login(cred: LoginCredentials):
    return {
        "username": cred.username,
        "password": cred.password
    }