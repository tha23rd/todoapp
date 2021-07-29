import hashlib
import os
from typing import Tuple

from fastapi import HTTPException
from fastapi.logger import logger
from rethinkdb import r
from rethinkdb.errors import ReqlOpFailedError

from app.database.base_store import BaseStore
from app.models.user import NewUserRequest
from app.models.user import User


def hash_password(
    raw_password: str, salt: bytes = os.urandom(32)
) -> Tuple[bytes, bytes]:
    key = hashlib.pbkdf2_hmac("sha256", raw_password.encode("utf-8"), salt, 100000)
    return key, salt


class UserStore(BaseStore):
    def __init__(self, conn_string: str, port: int) -> None:
        super().__init__(
            conn_string=conn_string, port=port, db_name="todos", table_name="users"
        )

    async def create_user(self, new_user: NewUserRequest) -> str:
        password_hash, salt = hash_password(new_user.raw_password)
        user = User(
            username=new_user.username,
            password_hash=password_hash,
            password_salt=salt,
            lists=[],
        )
        try:
            result = (
                await r.db(self._db_name)
                .table(self._table_name)
                .insert(user.dict(exclude_none=True))
                .run(self._conn)
            )
            if result["errors"] != 0:
                logger.error(f"DB request error: {result['first_error']}")
                raise HTTPException(
                    status_code=500,
                    detail=f"could not insert record into DB: User({user})",
                )
            return result["generated_keys"][0]
        except ReqlOpFailedError as err:
            logger.error(f"DB Error: {err}")
            raise HTTPException(
                status_code=500, detail=f"could not insert record into DB: User({user})"
            )
