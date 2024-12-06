from sqlmodel import Field, SQLModel, Relationship


class Task(SQLModel, table=True):
    id: int = Field(primary_key=True)
    title: str = Field(max_length=20)
    type: str = Field(max_length=20)
    weight: int = Field(default=0)
    ord_num: int = Field(max_length=20)
    col_id: int = Field(foreign_key="column.id")

    column: Column | None = Relationship(back_populates="tasks")

# TODO body_path
