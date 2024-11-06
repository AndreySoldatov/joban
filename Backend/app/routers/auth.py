from typing import Annotated
from app.routers.auth_db import User
from app.db import SessionDep
from pydantic import BaseModel

from sqlmodel import select
from fastapi import APIRouter, HTTPException, Depends, Response, Cookie
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from app.routers.auth_utils import gen_salt
import codecs
import hashlib

class DisplayName(BaseModel):
    display_name: str

router = APIRouter(prefix="/auth")

tokens = []

class Cookies(BaseModel):
    id_token: str = Field(validation_alias="DxpAccessToken")

async def check_token(cookies: Annotated[Cookies, Cookie()]):
    (_, exp_time) = codecs.decode(cookies.id_token, "hex").decode('utf-8').split('*')
    exp_time = datetime.fromisoformat(exp_time)
    if cookies.id_token in tokens:
        if datetime.now() >= exp_time:
            tokens.remove(cookies.id_token)
            raise HTTPException(status_code=401, detail="Token expired")
    else:
        raise HTTPException(status_code=401, detail="Not authorized")

@router.get("/protected", dependencies=[Depends(check_token)])
async def prot():
    return "authorized"

@router.get("/whoami", dependencies=[Depends(check_token)])
async def whoami(session: SessionDep, cookies: Annotated[Cookies, Cookie()]):
    (username, _) = codecs.decode(cookies.id_token, "hex").decode('utf-8').split('*')
    query = select(User).where(User.login == username)
    db_user = session.exec(query).first()
    return {"display_name": db_user.first_name + " " + db_user.last_name }

class UserRegisterRequest(BaseModel):
    first_name: str = Field(max_length=20)
    last_name: str = Field(max_length=30)
    login: str = Field(max_length=20, index=True)
    password: str = Field(max_length=16)

register_responses = {
    "201": {"description": "User Created"}, 
    "409": {"description": "User Already exists"}
}
@router.post("/register", status_code=201, responses=register_responses)
async def register(user: UserRegisterRequest, session: SessionDep) -> User:
    query = select(User).where(User.login == user.login)
    check_user = session.exec(query).first() #select предполагает возвращение неск. строчек. когда пишем фёст - берём 1 элемент массива
    if check_user:
        raise HTTPException(detail="User already exists", status_code=409)
    
    salt = gen_salt(16)
    hasher = hashlib.sha256()
    hasher.update((user.password + salt).encode())

    db_user = User(
        login = user.login,
        first_name = user.first_name,
        last_name = user.last_name,
        salt = salt,
        password_hash = hasher.hexdigest()
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def create_token(user: User) -> str:
    exp_time = datetime.now() + timedelta(hours=1)
    return (user.login + "*" + exp_time.isoformat()).encode('utf-8').hex()

class UserLoginRequest(BaseModel):
    login: str
    password: str

class DisplayName(BaseModel):
    display_name: str

login_responses = {
    "200": {"description": "Login Successful"}, 
    "401": {"description": "Invalid Credentials"}
}
@router.post("/login", status_code=200, responses=login_responses)
async def login(user: UserLoginRequest, session: SessionDep, response: Response) -> DisplayName:
    query = select(User).where(User.login == user.login)
    db_user = session.exec(query).first()
    if not db_user:
        raise HTTPException(detail="User not found", status_code=401)
    
    hasher = hashlib.sha256()
    hasher.update((user.password + db_user.salt).encode())
    if hasher.hexdigest() != db_user.password_hash:
        raise HTTPException(detail="Wrong password", status_code=401)

    token = create_token(user)
    tokens.append(token)
    
    response.set_cookie(key="DxpAccessToken", value=token)
    return {"display_name": db_user.first_name + " " + db_user.last_name }

@router.post("/logout", status_code=200, dependencies=[Depends(check_token)])
async def logout(cookies: Annotated[Cookies, Cookie()], response: Response):
    if cookies.id_token in tokens:
        tokens.remove(cookies.id_token)
    response.set_cookie(key="DxpAccessToken", value="")
    return "logout"

