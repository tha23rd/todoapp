from datetime import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from rethinkdb import r


class TempUser(BaseModel):
    id: Optional[str]
    registered_date: datetime = r.now()
    lists: List[str] = []


class User(BaseModel):
    id: Optional[str]
    registered_date: datetime = r.now()
    username: str
    password_hash: bytes
    password_salt: bytes
    lists: List[str] = []


class UserCreateResponse(BaseModel):
    id: str = Field(..., description="The id of the todolist that was created")


class NewUserRequest(BaseModel):
    username: str
    raw_password: str


class NewUserRegisterRequest(NewUserRequest):
    id: str
