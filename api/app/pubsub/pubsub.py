import asyncio
from typing import Any
from typing import Set

from fastapi.encoders import jsonable_encoder
from socketio import AsyncServer

from app.database.todo_store import TodoStore


class PubSub:

    subbed_channels: Set[str] = set()

    def __init__(self, sio: AsyncServer, todostore: TodoStore, namespace: str):
        self._sio = sio
        self._todostore = todostore
        self._ns = namespace

    async def _subscribe_to_todolist(self, todolist_id: str) -> Any:
        cursor = await self._todostore.get_todolist_cursor(todolist_id)
        while await cursor.fetch_next():
            item = await cursor.next()
            await self._sio.emit(
                "todo_list_change", jsonable_encoder(item), room=todolist_id
            )
            if self.room_is_empty(todolist_id):
                self.subbed_channels.remove(todolist_id)
                return

    def room_is_empty(self, room_id: str) -> Any:
        return len(self._sio.manager.rooms[self._ns][room_id]) == 0

    def subscribe_to_todolist(self, todolist_id: str) -> Any:
        if todolist_id not in self.subbed_channels:
            self.subbed_channels.add(todolist_id)
            asyncio.create_task(self._subscribe_to_todolist(todolist_id))
