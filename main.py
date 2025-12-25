from fastapi import FastAPI, UploadFile, Depends, Response
from io import BytesIO
from db import create_tables, get_conn
from tiktoken import encoding_for_model
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sentence_transformers import SentenceTransformer
from classes import file_and_question, pass_and_email
from utils import password_in_hash, auth, config, get_owner_id, verify_hash, check_current_token, validate_filename, get_user_dir,groq_client
import faiss,os
import numpy as np
from pathlib import Path



app=FastAPI()

enc=encoding_for_model("text-embedding-3-small")

emb_model = SentenceTransformer('all-MiniLM-L6-v2')

system_prompt="""
You are a context-bound assistant in a RAG system.
Use ONLY the provided context.
If the answer is not in the context, say:
"I don't know based on the provided documents."
"""

@app.get("/my_files")
async def all_files(current_user: str = Depends(check_current_token),uid: str = auth.CURRENT_SUBJECT, conn=Depends(get_conn)):
    owner_id=await get_owner_id(uid, conn)
    res=await conn.execute(text("SELECT * FROM files WHERE owner_id=:owner_id"), {"owner_id": owner_id})
    res = res.mappings().all()
    if not res:
        return {"msg":"no loaded files on server"}
    return res

@app.post("/sign_up")
async def sign_up(body:pass_and_email,conn=Depends(get_conn)):
    
    password_hash=password_in_hash(body.password)
    try:
        await conn.execute(text("""INSERT INTO users (email,password_hash) VALUES (:mail,:pass)"""),{"mail":body.email,"pass":password_hash})
    except IntegrityError as e:
        if "unique constraint" in str(e.orig):
            return {"error": "Email is already taken"}
    await conn.commit()
    return {"msg":"Succesful registation"}



@app.post("/log_in")
async def log_in(body:pass_and_email, response:Response, conn=Depends(get_conn)):
    res=await conn.execute(text("""SELECT password_hash FROM users WHERE email = :mail """),{"mail":body.email})
    hashed_pass=res.scalar_one_or_none()
    if not hashed_pass:
        return {"msg":f"no email as {body.email} in database"}
    if verify_hash(body.password,hashed_pass):
        token=auth.create_access_token(uid=body.email)
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
        return {"msg":"succesful log in, token has been added to your cookies"}
    else:
        return {"msg":"password or email is incorrect"}



@app.post("/addfile")
async def addfile(file:UploadFile,current_user: str = Depends(check_current_token),conn=Depends(get_conn), uid: str = auth.CURRENT_SUBJECT): #uid is email in my case
    file1=BytesIO(await file.read())
    if not file.filename.endswith(".txt"):
        return {"msg":"invalid file type, only .txt is allowed"}
    name=validate_filename(file.filename)
    tokenized_file=enc.encode(file1.getvalue().decode("utf-8"))
    
    chunk_size=300
    overlap=70
    chunks=[]
    for i in range(0,len(tokenized_file),chunk_size-overlap):
        chunk_tokenized=tokenized_file[i:i+chunk_size]
        chunk_text=enc.decode(chunk_tokenized)
        chunks.append(chunk_text)

    owner_id=await get_owner_id(uid,conn)
    res=await conn.execute(text("""INSERT INTO files (owner_id,name) VALUES (:id,:name) RETURNING id"""),{"id":owner_id,"name":name})
    
    file_id=res.scalar_one_or_none()
    chunk_ids = []
    for chunk in chunks:
        res_chunk = await conn.execute(text("""INSERT INTO chunks (file_id,chunk_content) VALUES (:file_id,:chunk_content) RETURNING id"""),
                                       {"file_id": file_id, "chunk_content": chunk})
        chunk_id = res_chunk.scalar_one_or_none()
        chunk_ids.append(chunk_id)

    embeddings = emb_model.encode(chunks)
    embedding_dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(embedding_dim)
    index = faiss.IndexIDMap(index)
    index.add_with_ids(np.array(embeddings, dtype='float32'), np.array(chunk_ids, dtype='int64'))

    dir = get_user_dir(owner_id)
    index_path = str(dir / f"index_faiss_{file_id}.faiss")
    faiss.write_index(index, index_path)
    await conn.commit()
    return {"msg":f"file added succesfully with id {file_id} and anme {name}"}
    


@app.delete("/delete_file")
async def delete_file(file_id: int,current_user: str = Depends(check_current_token), uid: str = auth.CURRENT_SUBJECT, conn=Depends(get_conn)):
    owner_id=await get_owner_id(uid,conn)
    res=await conn.execute(text("""DELETE FROM files WHERE id=:id and owner_id=:owner_id RETURNING id"""),{"id":file_id,"owner_id":owner_id})
    deleted_id=res.scalar_one_or_none()
    if deleted_id is None:
        return {"msg":f"file with id {file_id} not found or is not yours"}
    faiss_path = Path(f"data/users/user_{owner_id}/index_faiss_{file_id}.faiss")
    await conn.commit()
    if faiss_path.exists():
        os.remove(faiss_path)
    else:
        print(f"got trouble deleting faiss index with owner id {owner_id} and id file id {file_id}, path doesn't exist")
    return {"msg":f"file with id {deleted_id} has been deleted"}
    
    
    
@app.post("/chat")
async def chat(body:file_and_question,current_user: str = Depends(check_current_token), uid: str = auth.CURRENT_SUBJECT,conn=Depends(get_conn)):
    owner_id=await get_owner_id(uid,conn)
    res1=  await conn.execute(text("""SELECT * FROM files WHERE id=:id AND owner_id=:owner_id"""),{"id":body.file_id,"owner_id":owner_id})
    res1= res1.mappings().first()
    if not res1:
        return {"msg":"access to file denied or file not found"}
    faiss_path=f"data/users/user_{owner_id}/index_faiss_{body.file_id}.faiss"
    if not Path(faiss_path).exists():
        return {"msg":f"file with if {body.file_id} not found "}
    index=faiss.read_index(str(faiss_path))
    q_embedding=emb_model.encode([body.question]).astype("float32")
    d, i = index.search(q_embedding, k=4)
    chunks_text = []
    for chunk_id in i[0]:
        try:
            cid = int(chunk_id)
        except Exception:
            continue
        if cid == -1:
            continue
        res = await conn.execute(text("""SELECT chunk_content FROM chunks WHERE id=:id """), {"id": cid})
        chunk_content = res.scalar_one_or_none()
        if chunk_content:
            chunks_text.append(chunk_content)
    context = "\n\n".join(chunks_text)
    full_prompt=f"CONTEXT:{context}\n\nQUESTION:{body.question}"
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.1
    )
    return response.choices[0].message.content



@app.on_event("startup")
async def startup():
    await create_tables()

