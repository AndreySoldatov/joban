from typing import Annotated
from app.routers.auth_db import User, TokenStore
from app.db import SessionDep

from sqlmodel import select
from fastapi import APIRouter, HTTPException, Depends, Response, Cookie
from pydantic import Field
from datetime import datetime, timedelta
from app.routers.auth_utils import gen_salt
from app.dependencies import RestRequestModel
import hashlib
import os

router = APIRouter(prefix="/auth")


class Cookies(RestRequestModel):
    id_token: str = Field(validation_alias="DxpAccessToken")


async def check_token(cookies: Annotated[Cookies, Cookie()], session: SessionDep):
    """
    Validates the provided token from cookies and checks its expiration.

    Args:
        cookies (Annotated[Cookies, Cookie()]): Cookies object containing the token to validate.
        session (SessionDep): Database session dependency for querying and updating the token store.

    Raises:
        HTTPException: If the token is expired or not found, with status code 401.
    """
    token_record = session.exec(select(TokenStore).where(
        TokenStore.token == cookies.id_token)).first()
    if token_record:
        if datetime.now() >= datetime.fromisoformat(token_record.exp_time):
            session.delete(token_record)
            session.commit()
            raise HTTPException(status_code=401, detail="Token expired")
    else:
        raise HTTPException(status_code=401, detail="Not authorized")


@router.get("/protected", dependencies=[Depends(check_token)])
async def prot():
    return "authorized"


class DisplayName(RestRequestModel):
    display_name: str


@router.get("/whoami", dependencies=[Depends(check_token)])
async def whoami(session: SessionDep, cookies: Annotated[Cookies, Cookie()]) -> DisplayName:
    """
    Retrieves the display name of the authenticated user.

    Args:
        session (SessionDep): Database session dependency for querying user information.
        cookies (Annotated[Cookies, Cookie()]): Cookies object containing the token for user authentication.

    Returns:
        dict: A dictionary with the key "display_name" containing the user's full name.
    """
    if not cookies.id_token:
        raise HTTPException(status_code=401, detail="Token not provided")

    token_record = session.exec(select(TokenStore).where(
        TokenStore.token == cookies.id_token)).first()

    if not token_record:
        raise HTTPException(
            status_code=401, detail="Token is invalid or expired")

    db_user = session.exec(select(User).where(
        User.login == token_record.login)).first()
    return {"display_name": db_user.first_name + " " + db_user.last_name}


class UserRegisterRequest(RestRequestModel):
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
    """
    Registers a new user in the system.

    Args:
        user (UserRegisterRequest): User registration request containing login, password, and user details.
        session (SessionDep): Database session dependency for storing the new user.

    Returns:
        User: The newly registered user object.

    Raises:
        HTTPException: If the user already exists, with status code 409.
    """
    check_user = session.exec(select(User).where(
        User.login == user.login)).first()
    if check_user:
        raise HTTPException(detail="User already exists", status_code=409)

    salt = gen_salt(16)
    hasher = hashlib.sha256()
    hasher.update((user.password + salt).encode())

    db_user = User(
        login=user.login,
        first_name=user.first_name,
        last_name=user.last_name,
        salt=salt,
        password_hash=hasher.hexdigest()
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


class UserLoginRequest(RestRequestModel):
    login: str
    password: str


login_responses = {
    "200": {"description": "Login Successful"},
    "401": {"description": "Invalid Credentials"},
    "404": {"description": "User not found"}
}


@router.post("/login", status_code=200, responses=login_responses)
async def login(user: UserLoginRequest, session: SessionDep, response: Response) -> DisplayName:
    """
    Authenticates a user and generates an access token.

    This function verifies the user's credentials by comparing the provided password, salted and hashed, with the stored hash. 
    If valid, it generates a unique access token, stores it in the database with an expiration time, and sets it as a cookie 
    in the response.

    Args:
        user (UserLoginRequest): Login request containing the user's login and password.
        session (SessionDep): Database session dependency for user authentication and token storage.
        response (Response): Response object to set the authentication token as a cookie.

    Returns:
        DisplayName: A dictionary with the key "display_name" containing the user's full name.

    Raises:
        HTTPException: 
            - If the user is not found, with status code 404.
            - If the password is incorrect, with status code 401.
    """
    db_user = session.exec(select(User).where(
        User.login == user.login)).first()
    if not db_user:
        raise HTTPException(detail="User not found", status_code=404)

    hasher = hashlib.sha256()
    hasher.update((user.password + db_user.salt).encode())
    if hasher.hexdigest() != db_user.password_hash:
        raise HTTPException(detail="Wrong password", status_code=401)

    token = os.urandom(32).hex()
    session.add(TokenStore(
        login=user.login,
        token=token,
        exp_time=(datetime.now() + timedelta(hours=1)).isoformat()
    ))
    session.commit()

    response.set_cookie(
        key="DxpAccessToken",
        value=token,
        httponly=True,
        secure=True,
        samesite="None",
        max_age=3600,
        expires=(datetime.now() + timedelta(hours=1)).isoformat(),
    )
    return {"display_name": db_user.first_name + " " + db_user.last_name}


@router.post("/logout", status_code=200, dependencies=[Depends(check_token)])
async def logout(cookies: Annotated[Cookies, Cookie()], response: Response, session: SessionDep):
    token_record = session.exec(select(TokenStore).where(
        TokenStore.token == cookies.id_token)).first()
    if token_record:
        session.delete(token_record)
        session.commit()

    response.set_cookie(
        key="DxpAccessToken",
        value="",
        httponly=True,
        secure=True,
        samesite="None",
        max_age=0,
        expires="Thu, 01 Jan 1970 00:00:00 GMT",
    )
    return "logout"
