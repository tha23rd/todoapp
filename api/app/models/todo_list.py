import uuid
from datetime import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from rethinkdb import r


class TodoItem(BaseModel):
    id: str = uuid.uuid1().hex
    created_date: datetime = r.now()
    created_by: Optional[str]  # user_id, for now could be optional?
    name: str
    is_complete: bool = False


class TodoList(BaseModel):
    id: Optional[str]
    name: str
    created_date: datetime = r.now()
    updated_date: datetime = r.now()
    items: List[TodoItem] = []


class TodoListRename(BaseModel):
    name: str


class TodoListCreateResponse(BaseModel):
    id: str = Field(..., description="The id of the todolist that was created")
