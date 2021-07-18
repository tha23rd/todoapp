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
    created_by: str  # user_id, for now could be optional?
    content: str
    is_complete: bool = False


class TodoList(BaseModel):
    id: Optional[str]
    name: str
    created_date: datetime = r.now()
    updated_date: datetime = r.now()
    items: List[TodoItem] = []


class TodoListCreateResponse(BaseModel):
    id: str = Field(..., description="The id of the todolist that was created")
