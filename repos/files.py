from sqlalchemy import text


async def insert_file(owner_id, name, conn):
    res = await conn.execute(text("""INSERT INTO files (owner_id,name) VALUES (:id,:name) RETURNING id"""),
                             {"id": owner_id, "name": name})
    return res.scalar_one_or_none()


async def insert_chunk(file_id, chunk_content, conn):
    res = await conn.execute(text("""INSERT INTO chunks (file_id,chunk_content) VALUES (:file_id,:chunk_content) RETURNING id"""),
                             {"file_id": file_id, "chunk_content": chunk_content})
    return res.scalar_one_or_none()

async def select_pass_hash(email,conn):
    res = await conn.execute(text("""SELECT password_hash FROM users WHERE email = :email """),{"email": email})
    return res.scalar_one_or_none()

async def insert_user(email,password_hash,conn):
    await conn.execute(text("""INSERT INTO users (email,password_hash) VALUES (:email,:pass)"""),
                           {"email":email, "pass": password_hash})
    
async def select_files(owner_id,conn):
    res = await conn.execute(text("SELECT * FROM files WHERE owner_id=:owner_id"), {"owner_id": owner_id})
    return res.mappings().all()

async def get_owner_id(email,conn):
    res = await conn.execute(text("""SELECT id FROM users WHERE email=:email"""),{"email": email})
    owner_id = res.scalar_one_or_none()
    return owner_id

async def select_file_with_id(file_id,owner_id,conn):
    res = await conn.execute(text("""SELECT * FROM files WHERE id=:id AND owner_id=:owner_id"""), {"id": file_id, "owner_id": owner_id})
    return res.mappings().first()

async def select_chunk_text(cid,conn):
    res = await conn.execute(text("""SELECT chunk_content FROM chunks WHERE id=:id """), {"id": cid})
    return res.scalar_one_or_none()

async def delete_file(file_id,owner_id,conn):
    res = await conn.execute(text("""DELETE FROM files WHERE id=:id and owner_id=:owner_id RETURNING id"""), {"id": file_id, "owner_id": owner_id})
    return res.scalar_one_or_none()