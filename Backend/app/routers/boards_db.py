from sqlmodel import Field, SQLModel, Relationship


class Board(SQLModel, table=True):
    id: int = Field(primary_key=True)
    title: str = Field(max_length=20)

    columns: list["Column"] = Relationship(back_populates="board")


class Column(SQLModel, table=True):
    id: int = Field(primary_key=True)
    board_id: int = Field(foreign_key="board.id")
    title: str = Field(max_length=20)
    ord_num: int = Field(default=0)

    tasks: list["Task"] = Relationship(back_populates="column")
    board: Board | None = Relationship(back_populates="columns")


class Task(SQLModel, table=True):
    id: int = Field(primary_key=True)
    title: str = Field(max_length=20)
    type: str = Field(max_length=20)
    weight: int = Field(default=0)
    ord_num: int = Field(max_length=20)
    col_id: int = Field(foreign_key="column.id")

    column: Column | None = Relationship(back_populates="tasks")
