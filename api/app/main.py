import urllib.parse
from typing import Any

import socketio
from fastapi import FastAPI
from fastapi.logger import logger
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.todo_store import TodoStore
from app.models.todo_list import Path
from app.models.todo_list import TodoListCreateResponse
from app.models.todo_list import TodoListEdit
from app.models.todo_list import TodoListNewItem
from app.pubsub.pubsub import PubSub

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

sio = socketio.AsyncServer(cors_allowed_origins=[], async_mode="asgi")
sio_app = socketio.ASGIApp(sio)
ws_namespace = "/"

logger.error([str(origin) for origin in settings.BACKEND_CORS_ORIGINS])

app.mount("/ws", app=sio_app)

DATABASE_HOST = settings.RDB_SERVER
DATABASE_PORT = settings.RDB_PORT
logger.info(f"DB host: {DATABASE_HOST}, DB port: {DATABASE_PORT}")
todo_store = TodoStore(conn_string=DATABASE_HOST, port=DATABASE_PORT)
pubsub = PubSub(sio, todo_store, ws_namespace)


@app.on_event("startup")
async def startup_event() -> Any:
    await todo_store.setup_db()


@app.on_event("shutdown")
async def shutdown_event() -> Any:
    await todo_store.close_connection()


@app.post("/todolist/", response_model=TodoListCreateResponse)
async def read_item() -> Any:
    return TodoListCreateResponse(id=await todo_store.create_todo_list())


@app.get("/todolist/{list_id}")
async def get_list(list_id: str) -> Any:
    return await todo_store.get_todo_list(list_id)


@app.patch("/todolist/{list_id}")
async def edit_list(list_id: str, edit: TodoListEdit) -> Any:
    if edit.path == Path.COMPLETE_ITEM:
        await todo_store.complete_todo_item(list_id, edit)
    if edit.path == Path.RENAME_LIST:
        await todo_store.rename_list(list_id, edit)


@app.delete("/todolist/{list_id}")
async def delete_list(list_id: str, edit: TodoListEdit) -> Any:
    if edit.path == Path.DELETE_LIST:
        await todo_store.delete_todo_list(list_id)
    if edit.path == Path.DELETE_ITEM:
        await todo_store.delete_todo_item(list_id, edit)


@sio.event
async def connect(sid: Any, environ: Any) -> Any:
    query = urllib.parse.parse_qs(environ["QUERY_STRING"])
    if len(query["roomName"]) > 0:
        logger.error("Adding connection to room: " + query["roomName"][0])
        sio.enter_room(sid, query["roomName"][0])
        pubsub.subscribe_to_todolist(query["roomName"][0])
    await sio.save_session(sid, {"username": "test"})


@app.post("/todolist/{list_id}/")
async def create_item(list_id: str, new_item: TodoListNewItem) -> Any:
    await todo_store.create_todo_item(list_id, new_item)


@app.get("/trigger/")
async def trigger() -> Any:
    # this is test method used to trigger websocket event
    logger.error(sio.manager.rooms["/"].keys())
    await sio.emit(
        "message", {"message": "hello!"}, room="ad509ce8-daee-4084-b5d0-df3f0c15e398"
    )
