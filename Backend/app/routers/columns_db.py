from sqlmodel import Field, SQLModel, Relationship

class Column(SQLModel, table=True):
    id: int = Field(primary_key=True)
    board_id: int = Field(foreign_key="board.id")
    title: str = Field(max_length=20)
    ord_num: int = Field(default=0)
