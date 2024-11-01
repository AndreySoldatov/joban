from typing import Annotated
from app.routers.auth_db import User
from app.db import SessionDep

from sqlmodel import select
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, HTTPException, Depends

router = APIRouter(prefix="/auth")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/protected")
async def prot(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}

register_responses = {
    "201": {"description": "User Created"}, 
    "409": {"description": "User Already exists"}
}
@router.post("/register", status_code=201, responses=register_responses)
async def register(user: User, session: SessionDep) -> User:
    query = select(User).where(User.login == user.login)
    db_user = session.exec(query).first() #select предполагает возвращение неск. строчек. когда пишем фёст - берём 1 элемент массива
    if db_user:
        raise HTTPException(detail="User already exists", status_code=409)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

login_responses = {
    "200": {"description": "Login Successful"}, 
    "401": {"description": "Invalid Credentials"}
}
@router.post("/login", status_code=200, responses=login_responses)
async def login(user: User, session: SessionDep) -> dict:
    query = select(User).where(User.login == user.login)
    db_user = session.exec(query).first()
    if not db_user:
        raise HTTPException(detail="User not found", status_code=401)
    if user.password != db_user.password:
        raise HTTPException(detail="Wrong password", status_code=401)
    displayName = db_user.first_name + " " + db_user.last_name
    response_data = {
        "displayName": displayName
    }
    return response_data
