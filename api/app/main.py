from typing import Any

from fastapi import FastAPI
from fastapi.logger import logger

from app.core.config import settings
from app.database.todo_store import TodoStore
from app.models.todo_list import TodoListCreateResponse

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

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
async def read_item() -> Any:
    return TodoListCreateResponse(id=await todo_store.create_todo_list())


@app.patch("/todolist/{list_id}/{new_name}")
async def rename_list(list_id: str, new_name: str) -> Any:
    await todo_store.rename_list(list_id, new_name)
