from datetime import datetime
from typing import List

from pydantic import BaseModel
from rethinkdb import r


class TodoUser(BaseModel):
    registered_date: datetime = r.now()
    username: str
    password_hash: str
    lists: List[str]
