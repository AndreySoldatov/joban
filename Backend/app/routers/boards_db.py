from sqlmodel import Field, SQLModel


class Board(SQLModel, table=True):
    id: int = Field(primary_key=True)
    title: str = Field(max_length=20)

    columns: list["Column"] = Relationship(back_populates="board")
