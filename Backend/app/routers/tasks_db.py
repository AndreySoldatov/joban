from sqlmodel import Field, SQLModel, Relationship

class Task(SQLModel, table=True):
    id: int = Field(primary_key=True)
    col_id: int = Field(foreign_key="column.id")
    title: str = Field(max_length=20)
    type: str = Field(max_length=20)
    weight: int = Field(default=0)
