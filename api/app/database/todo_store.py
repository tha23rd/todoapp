from typing import Any

from fastapi import HTTPException
from fastapi.logger import logger
from rethinkdb import r
from rethinkdb.errors import ReqlDriverError
from rethinkdb.errors import ReqlOpFailedError

from app.models.todo_list import TodoList

r.set_loop_type("asyncio")
default_todo_list_name = "My New Todo List"
db_name = "todos"
db_table = "todolists"


class TodoStore:
    def __init__(self, conn_string: str, port: int) -> None:
        self._conn_string = conn_string
        self._port = port
        self._db_is_setup = False
        self._conn = None  # Connection not setup

    async def setup_db(self) -> Any:
        try:
            self._conn = await r.connect(self._conn_string, self._port)
            if "todos" not in await r.db_list().run(self._conn):  # setup db and tables
                await r.db_create("todos").run(self._conn)
                await r.db(db_name).table_create(db_table).run(self._conn)
        except ReqlDriverError as err:
            logger.warning(f"Could not connect to DB: {err}")
        except ReqlOpFailedError as ex:
            logger.warning(f"DB creation error: {ex}")
        self._db_is_setup = True

    async def close_connection(self) -> Any:
        if self._conn:
            await self._conn.close()

    async def create_todo_list(self) -> str:
        todo_list = TodoList(name=default_todo_list_name)
        try:
            result = (
                await r.db(db_name)
                .table(db_table)
                .insert(todo_list.dict(exclude_none=True))
                .run(self._conn)
            )
            if result["errors"] != 0:
                logger.error(f"DB request error: {result['first_error']}")
                raise HTTPException(
                    status_code=500,
                    detail=f"could not insert record into DB: TodoList({todo_list})",
                )
            return result["generated_keys"][0]
        except ReqlOpFailedError as err:
            logger.error(f"DB Error: {err}")
            raise HTTPException(
                status_code=500,
                detail=f"could not insert record into DB: TodoList({todo_list})",
            )