import urllib.parse
from typing import Any

import socketio
from fastapi import FastAPI
from fastapi.logger import logger
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.todo_store import TodoStore
from app.models.todo_list import TodoListCreateResponse
from app.pubsub.pubsub import PubSub

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_methods=["*"],
    allow_headers=["*"],
)

sio = socketio.AsyncServer(cors_allowed_origins=[], async_mode="asgi")
sio_app = socketio.ASGIApp(sio)
ws_namespace = "/"


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
async def create_todolist() -> Any:
    return TodoListCreateResponse(id=await todo_store.create_todo_list())


@sio.event
async def connect(sid: Any, environ: Any) -> Any:
    query = urllib.parse.parse_qs(environ["QUERY_STRING"])
    if len(query["roomName"]) > 0:
        logger.error("Adding connection to room: " + query["roomName"][0])
        sio.enter_room(sid, query["roomName"][0])
        pubsub.subscribe_to_todolist(query["roomName"][0])
    await sio.save_session(sid, {"username": "test"})


@app.post("/todolist/{list_id}/{item_name}")
async def create_item(list_id: str, item_name: str) -> Any:
    await todo_store.create_todo_item(list_id, item_name)


@app.get("/trigger/")
async def trigger() -> Any:
    # this is test method used to trigger websocket event
    logger.error(sio.manager.rooms["/"].keys())
    await sio.emit(
        "message", {"message": "hello!"}, room="ad509ce8-daee-4084-b5d0-df3f0c15e398"
    )
