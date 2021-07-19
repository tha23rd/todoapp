from typing import Any

import socketio
from fastapi import FastAPI
from fastapi.logger import logger

from app.core.config import settings
from app.database.todo_store import TodoStore
from app.models.todo_list import TodoListCreateResponse

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
sio_app = socketio.ASGIApp(sio)

app.mount("/ws", app=sio_app)

DATABASE_HOST = settings.RDB_SERVER
DATABASE_PORT = settings.RDB_PORT
logger.info(f"DB host: {DATABASE_HOST}, DB port: {DATABASE_PORT}")
todo_store = TodoStore(conn_string=DATABASE_HOST, port=DATABASE_PORT)


@app.on_event("startup")
async def startup_event() -> Any:
    await todo_store.setup_db()


@app.on_event("shutdown")
async def shutdown_event() -> Any:
    await todo_store.close_connection()


@app.post("/todolist/", response_model=TodoListCreateResponse)
async def create_todolist() -> Any:
    return TodoListCreateResponse(id=await todo_store.create_todo_list())


@sio.event
async def connect(sid: Any, environ: Any) -> Any:
    logger.error(environ)
    await sio.save_session(sid, {"username": "test"})


@sio.event
async def message(sid: Any, data: Any) -> Any:
    session = await sio.get_session(sid)
    print("message from ", session["username"])


@app.post("/todolist/{list_id}/{item_name}")
async def create_item(list_id: str, item_name: str) -> Any:
    await todo_store.create_todo_item(list_id, item_name)


@app.get("/trigger/")
async def trigger() -> Any:
    await sio.emit("message", {"message": "hello!"})
