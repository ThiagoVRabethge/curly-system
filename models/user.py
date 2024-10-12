from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    email: str = Field(index=True, unique=True)
    password: str

    def to_dict(self):
        return {"id": self.id, "username": self.username, "email": self.email}


class Login(BaseModel):
    username: str
    password: str
