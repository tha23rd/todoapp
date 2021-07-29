from typing import Any

from fastapi.logger import logger
from rethinkdb import r
from rethinkdb.errors import ReqlDriverError
from rethinkdb.errors import ReqlOpFailedError

r.set_loop_type("asyncio")


# Inherit the stuff that seems like could be useful.
class BaseStore:
    def __init__(
        self, conn_string: str, port: int, db_name: str, table_name: str
    ) -> None:
        self._conn_string = conn_string
        self._port = port
        self._db_is_setup = False
        self._conn = None  # Connection not setup
        self._db_name = db_name
        self._table_name = table_name

    async def setup_db(self) -> Any:
        try:
            self._conn = await r.connect(self._conn_string, self._port)
            if self._db_name not in await r.db_list().run(
                self._conn
            ):  # setup db and tables
                await r.db_create(self._db_name).run(self._conn)
                await r.db(self._db_name).table_create(self._table_name).run(self._conn)
            elif self._table_name not in await r.db(self._db_name).table_list().run(
                self._conn
            ):
                await r.db(self._db_name).table_create(self._table_name).run(self._conn)
        except ReqlDriverError as err:
            logger.warning(f"Could not connect to DB: {err}")
        except ReqlOpFailedError as ex:
            logger.warning(f"DB creation error: {ex}")
        self._db_is_setup = True

    async def close_connection(self) -> Any:
        if self._conn:
            await self._conn.close()

    # Don't know what this does. is it necessary for something, or only for the lists?
    # async def get_cursor(self, item_id: str) -> Any:
    #     try:
    #         cursor = (
    #             await r.db(self._db_name)
    #             .table(self._table_name)
    #             .get(item_id)
    #             .changes()
    #             .run(self._conn)
    #         )
    #         return cursor
    #     except Exception:
    #         logger.error(f"Failed to get the cursor for item: {item_id}")
