from sqlmodel import Field, Relationship, SQLModel, Relationship


class Column(SQLModel, table=True):
    id: int = Field(primary_key=True)
    board_id: int = Field(foreign_key="board.id")
    title: str = Field(max_length=20)
    ord_num: int = Field(default=0)

    tasks: list["Task"] = Relationship(back_populates="column")
    board: Board | None = Relationship(back_populates="columns")
