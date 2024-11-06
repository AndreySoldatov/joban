from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    first_name: str = Field(max_length=20)
    last_name: str = Field(max_length=30)
    login: str = Field(max_length=20, index=True)
    password_hash: str = Field(max_length=64)
    salt: str = Field(max_length=16)