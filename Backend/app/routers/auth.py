from typing import Annotated
from app.routers.auth_db import User
from app.db import SessionDep

from sqlmodel import select
from fastapi import APIRouter, HTTPException, Depends, Response, Cookie
from pydantic import Field
from datetime import datetime, timedelta, timezone
from app.routers.auth_utils import gen_salt
from app.dependencies import RestRequestModel
import codecs
import hashlib

router = APIRouter(prefix="/auth")

tokens = []


class Cookies(RestRequestModel):
    id_token: str = Field(validation_alias="DxpAccessToken")


async def check_token(cookies: Annotated[Cookies, Cookie()]):
    """
    Validates the user's token.

    This function checks if the token from the cookies is valid, unexpired, 
    and present in the global token list.

    Args:
        cookies (Cookies): The user's cookies, including the `id_token`.

    Raises:
        HTTPException: 
            - 401 Unauthorized if the token is expired.
            - 401 Unauthorized if the token is not found in the global list.

    Notes:
        - Expired tokens are automatically removed from the global list.
    """

    (_, exp_time) = codecs.decode(
        cookies.id_token, "hex").decode('utf-8').split('*')
    exp_time = datetime.fromisoformat(exp_time)
    if cookies.id_token in tokens:
        if datetime.now(timezone.utc) >= exp_time:
            tokens.remove(cookies.id_token)
            raise HTTPException(
                status_code=401,
                detail="Token expired"
            )
    else:
        raise HTTPException(status_code=401, detail="Not authorized")


@router.get("/protected", dependencies=[Depends(check_token)])
async def prot():
    return "authorized"


@router.get("/whoami", dependencies=[Depends(check_token)])
async def whoami(session: SessionDep, cookies: Annotated[Cookies, Cookie()]):
    """
    Retrieves the currently logged-in user's display name.

    This endpoint decodes the token to identify the user and fetches their 
    details from the database.

    Args:
        session (SessionDep): A database session for querying user data.
        cookies (Cookies): The user's cookies, including the `id_token`.

    Returns:
        dict: A dictionary containing the user's display name 
            (first and last name combined).

    Notes:
        - Requires a valid token (enforced by `check_token`).
    """

    (username, _) = codecs.decode(
        cookies.id_token, "hex").decode('utf-8').split('*')
    query = select(User).where(User.login == username)
    db_user = session.exec(query).first()
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

    This endpoint creates a new user by validating the input, checking for 
    existing users with the same login, and securely hashing the password. 
    If successful, the new user is stored in the database and returned.

    Args:
        user (UserRegisterRequest): An object containing the registration 
            details such as login, password, first name, and last name.
        session (SessionDep): A database session dependency for interacting 
            with the database.

    Returns:
        User: The newly created user object.

    Raises:
        HTTPException: If a user with the same login already exists (409 
            Conflict).

    Notes:
        - Passwords are hashed with a generated salt using SHA-256 before 
        storage.
        - The function raises a 409 HTTP status code if a user with the 
        given login already exists.
    """

    query = select(User).where(User.login == user.login)
    check_user = session.exec(query).first()
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


def create_token(user: User) -> str:
    """
    Generates a simple token for a given user.

    This function creates a token by combining the user's login with an 
    expiration time (1 hour from the current time) and encoding the result 
    as a hexadecimal string.

    Args:
        user (User): The user object for whom the token is generated. 
            The `login` attribute of the user is used in the token.

    Returns:
        str: A hexadecimal-encoded string representing the token.
    """

    exp_time = datetime.now(timezone.utc) + timedelta(hours=1)
    return (user.login + "*" + exp_time.isoformat()).encode('utf-8').hex()


class UserLoginRequest(RestRequestModel):
    login: str
    password: str


class DisplayName(RestRequestModel):
    display_name: str


login_responses = {
    "200": {"description": "Login Successful"},
    "401": {"description": "Invalid Credentials"},
    "404": {"description": "User not found"}
}


@router.post("/login", status_code=200, responses=login_responses)
async def login(user: UserLoginRequest, session: SessionDep, response: Response) -> DisplayName:
    """
    Handles user login and authentication.

    This endpoint validates a user's login credentials. If the credentials 
    are correct, it generates a token, stores it in a global token list, 
    sets it as a cookie, and returns the user's display name.

    Args:
        user (UserLoginRequest): An object containing the login credentials, 
            including the login and password.
        session (SessionDep): A database session dependency for interacting 
            with the database.
        response (Response): The HTTP response object for setting cookies.

    Returns:
        DisplayName: A dictionary containing the user's display name 
            (first and last name combined).

    Raises:
        HTTPException: 
            - If the user is not found (404 Not Found).
            - If the password is incorrect (401 Unauthorized).

    Side Effects:
        - Sets a cookie `DxpAccessToken` in the response with the generated 
        token.
        - Appends the token to the global `tokens` list.

    Notes:
        - Passwords are hashed with the stored salt using SHA-256 and 
        compared to the stored hash for validation.
    """

    query = select(User).where(User.login == user.login)
    db_user = session.exec(query).first()
    if not db_user:
        raise HTTPException(detail="User not found", status_code=404)

    hasher = hashlib.sha256()
    hasher.update((user.password + db_user.salt).encode())
    if hasher.hexdigest() != db_user.password_hash:
        raise HTTPException(detail="Wrong password", status_code=401)

    token = create_token(user)
    tokens.append(token)

    response.set_cookie(key="DxpAccessToken", value=token)
    return {"display_name": db_user.first_name + " " + db_user.last_name}


@router.post("/logout", status_code=200, dependencies=[Depends(check_token)])
async def logout(cookies: Annotated[Cookies, Cookie()], response: Response):
    """
    Logs out the user by invalidating their token.

    This endpoint removes the user's token from the global token list and 
    clears the `DxpAccessToken` cookie.

    Args:
        cookies (Cookies): The user's cookies, including the `id_token`.
        response (Response): The HTTP response object for clearing cookies.

    Returns:
        str: A message confirming logout.

    Notes:
        - Requires a valid token to access (enforced by `check_token`).
        - Token management is handled via a global list.
    """

    if cookies.id_token in tokens:
        tokens.remove(cookies.id_token)
    response.set_cookie(key="DxpAccessToken", value="")
    return "logout"
