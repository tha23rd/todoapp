import hashlib
import os
from typing import Any
from typing import Tuple

from fastapi import HTTPException
from fastapi.logger import logger
from rethinkdb import r
from rethinkdb.errors import ReqlOpFailedError

from app.database.base_store import BaseStore
from app.models.user import NewUserRegisterRequest
from app.models.user import NewUserRequest
from app.models.user import TempUser
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
            username=new_user.username, password_hash=password_hash, password_salt=salt
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

    async def create_temp_user(self) -> str:
        temp_user = TempUser()
        try:
            result = (
                await r.db(self._db_name)
                .table(self._table_name)
                .insert(temp_user.dict(exclude_none=True))
                .run(self._conn)
            )
            if result["errors"] != 0:
                logger.error(f"DB request error: {result['first_error']}")
                raise HTTPException(
                    status_code=500,
                    detail=f"could not insert record into DB: TempUser({temp_user})",
                )
            return result["generated_keys"][0]
        except ReqlOpFailedError as err:
            logger.error(f"DB Error: {err}")
            raise HTTPException(
                status_code=500,
                detail=f"could not insert record into DB: User({temp_user})",
            )

    async def register_temp_user(self, new_user: NewUserRegisterRequest) -> str:
        password_hash, salt = hash_password(new_user.raw_password)
        try:
            user = (
                await r.db(self._db_name)
                .table(self._table_name)
                .get(new_user.id)
                .run(self._conn)
            )
            if not user:
                raise HTTPException(
                    status_code=404,
                    detail=f"could not find temp_user id: {new_user.id}",
                )
            if "username" in user:
                raise HTTPException(
                    status_code=403, detail=f"user {new_user.id} has already registered"
                )
            result = (
                await r.db(self._db_name)
                .table(self._table_name)
                .get(new_user.id)
                .update(
                    {
                        "username": new_user.username,
                        "password_hash": password_hash,
                        "password_salt": salt,
                    }
                )
                .run(self._conn)
            )
        except ReqlOpFailedError as err:
            logger.error(f"DB Error: {err}")
            raise HTTPException(
                status_code=500,
                detail=f"could not convert record into DB: User({new_user})",
            )
        if "skipped" in result and result["skipped"] != 0:
            raise HTTPException(
                status_code=404, detail=f"could not find temp_user id: {new_user.id}"
            )
        if "replaced" in result and result["replaced"] == 1:
            return new_user.id
        else:
            raise HTTPException(status_code=500, detail="not sure what messed up")

    async def add_list_to_user(self, list_id: str, user_id: str) -> Any:
        try:
            result = (
                await r.db(self._db_name)
                .table(self._table_name)
                .get(user_id)
                .update({"lists": r.row["lists"].append(list_id)})
                .run(self._conn)
            )
        except ReqlOpFailedError as err:
            logger.error(f"DB Error: {err}")
            raise HTTPException(
                status_code=500,
                detail=f"could not add TodoList({list_id}) to User({user_id})",
            )
        if "skipped" in result and result["skipped"] != 0:
            raise HTTPException(
                status_code=404, detail=f"could not find temp_user id: {user_id}"
            )
