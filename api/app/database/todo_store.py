from typing import Any

from fastapi import HTTPException
from fastapi.logger import logger
from rethinkdb import r
from rethinkdb.errors import ReqlDriverError
from rethinkdb.errors import ReqlOpFailedError

from app.models.todo_list import TodoItem
from app.models.todo_list import TodoList
from app.models.todo_list import TodoListEdit
from app.models.todo_list import TodoListNewItem

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

    async def rename_list(self, list_id: str, new_name: TodoListEdit) -> Any:
        try:
            result = (
                await r.db(db_name)
                .table(db_table)
                .get(list_id)
                .update({"name": new_name.name})
                .run(self._conn)
            )
        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=500,
                detail=f"could not rename record in DB: TodoList({list_id})",
            )
        if result["errors"] != 0:
            logger.error(f"DB request error: {result['first_error']}")
            raise HTTPException(
                status_code=500,
                detail=f"could not rename record in DB: TodoList({list_id})",
            )
        if result["skipped"] != 0:
            logger.error(f"Skipped rename on list_id: {list_id}")
            raise HTTPException(
                status_code=404,
                detail=f"could not find record in DB: TodoList({list_id})",
            )

    async def get_todo_list(self, list_id: str) -> Any:
        try:
            result: TodoList = (
                await r.db(db_name).table(db_table).get(list_id).run(self._conn)
            )
        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=500,
                detail=f"server error while getting record from DB: TodoList({list_id})",
            )
        if result is None:
            logger.error(f"could not find todolist: {list_id}")
            raise HTTPException(
                status_code=404, detail=f"could not find todolist: {list_id}"
            )
        return result

    async def delete_todo_list(self, list_id: str) -> Any:
        try:
            result = (
                await r.db(db_name)
                .table(db_table)
                .get(list_id)
                .delete()
                .run(self._conn)
            )
        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=500,
                detail=f"server error while deleting record from DB: TodoList({list_id})",
            )
        if result["errors"] != 0:
            logger.error(f"DB request error: {result['first_error']}")
            raise HTTPException(
                status_code=500,
                detail=f"could not delete record from DB: TodoList({list_id})",
            )
        if result["skipped"] != 0:
            logger.error(result["skipped"])
            raise HTTPException(
                status_code=404,
                detail=f"could not find record in DB: TodoList({list_id})",
            )

    async def create_todo_item(self, list_id: str, item: TodoListNewItem) -> Any:
        todo_item = TodoItem(name=item.name)
        try:
            result = (
                await r.db(db_name)
                .table(db_table)
                .get(list_id)
                .update({"items": r.row["items"].append(todo_item.dict())})
                .run(self._conn)
            )
        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=500,
                detail=f"could not insert record into DB: TodoItem({todo_item})",
            )
        if result["errors"] != 0:
            logger.error(f"DB request error: {result['first_error']}")
            raise HTTPException(
                status_code=500,
                detail=f"could not insert record into DB: TodoItem({todo_item})",
            )
        if result["skipped"] != 0:
            logger.error(result["skipped"])
            raise HTTPException(
                status_code=404, detail=f"could not find todolist: {list_id}"
            )

    async def complete_todo_item(self, list_id: str, item: TodoListEdit) -> Any:
        try:
            result = (
                await r.db(db_name)
                .table(db_table)
                .get(list_id)
                .update(
                    {
                        "items": r.row["items"].map(
                            lambda ele: r.branch(
                                ele["id"].eq(item.id),
                                ele.merge({"is_complete": item.is_complete}),
                                ele,
                            )
                        )
                    }
                )
                .run(self._conn)
            )
        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=500, detail=f"could not complete record in DB: {item.id}"
            )
        if result["errors"] != 0:
            logger.error(f"DB request error: {result['first_error']}")
            raise HTTPException(
                status_code=500,
                detail=f"could not change status of record in DB: TodoItem({item.id})",
            )
        if result["skipped"] != 0 or result["replaced"] == 0:
            logger.error(result["skipped"])
            raise HTTPException(
                status_code=404,
                detail=f"could not find item or todolist: {list_id}, {item.id}",
            )

    async def get_todolist_cursor(self, todolist_id: str) -> Any:
        try:
            cursor = (
                await r.db(db_name)
                .table(db_table)
                .get(todolist_id)
                .changes()
                .run(self._conn)
            )
            return cursor
        except Exception:
            logger.error(f"Failed to get the todolist cursor for: {todolist_id}")
