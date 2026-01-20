from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
import os

load_dotenv()
db_url = os.getenv("DB_URL")

engine = create_async_engine(db_url)

async def get_conn():
    async with engine.connect() as conn:
        try:
            yield conn
        finally:
            await conn.close()

async def create_tables():
    async with engine.begin() as conn:
        await conn.execute(text("""CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL)"""))
        await conn.execute(text("""CREATE TABLE IF NOT EXISTS files(
            id SERIAL PRIMARY KEY,
            owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            name TEXT NOT NULL)"""))
        await conn.execute(text("""CREATE TABLE IF NOT EXISTS chunks(
            id SERIAL PRIMARY KEY,
            file_id INTEGER REFERENCES files(id) ON DELETE CASCADE,
            chunk_content TEXT)"""))