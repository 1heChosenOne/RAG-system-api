from fastapi import FastAPI
from db import create_tables
import routes.files
from exception_handlers import register_handlers


app=FastAPI()

app.include_router(routes.files.router)
register_handlers(app)


@app.on_event("startup")
async def startup():
    await create_tables()

