from fastapi import UploadFile, HTTPException
from io import BytesIO
from utils import enc, validate_filename, system_prompt
from repos import files as files_repo
from infra import indexer, embeddings as embedder, groq as groq_infra
from pathlib import Path
import os



def chunk_text_from_bytes(file_bytes, chunk_size=300, overlap=70): # chunk_size and verlap are customizable
	tokenized_file = enc.encode(file_bytes.getvalue().decode("utf-8"))
	chunks = []
	for i in range(0, len(tokenized_file), chunk_size - overlap):
		chunk_tokenized = tokenized_file[i:i + chunk_size]
		chunk_text = enc.decode(chunk_tokenized)
		chunks.append(chunk_text)
	return chunks



async def addfile(file: UploadFile, uid: str, conn):
	file_bytes = BytesIO(await file.read())

	if not file.filename.endswith(".txt"):
		raise HTTPException(status_code=400, detail="invalid file type, only .txt is allowed")

	name = validate_filename(file.filename)

	chunks = chunk_text_from_bytes(file_bytes)

	owner_id = await files_repo.get_owner_id(uid, conn)

	file_id = await files_repo.insert_file(owner_id, name, conn)

	chunk_ids = []
	for chunk in chunks:
		cid = await files_repo.insert_chunk(file_id, chunk, conn)
		chunk_ids.append(cid)

	embeddings = embedder.np_embed_texts(chunks)
	indexer.write_index(owner_id, file_id, embeddings, chunk_ids)

	await conn.commit()
	return {"msg": f"file added succesfully with id {file_id} and name {name}"}



async def all_files(uid: str, conn):
    owner_id = await files_repo.get_owner_id(uid, conn)
    res = await files_repo.select_files(owner_id,conn)
    
    if not res:
        return {"msg":"no loaded files on server"}
    return res



async def chat(question, file_id, uid, conn):
    
	owner_id = await files_repo.get_owner_id(uid, conn)
	res = await files_repo.select_file_with_id(file_id, owner_id, conn)
 
	if not res:
		return {"msg": "access to file denied or file not found"}
	faiss_path = f"data/users/user_{owner_id}/index_faiss_{file_id}.faiss"
 
	if not Path(faiss_path).exists():
		return {"msg": f"file with id {file_id} not found in memory"}

	index = indexer.index_load(faiss_path)
	q_embedding = embedder.embed_text(question)
	i =  indexer.index_search(index,q_embedding)
 
	chunks_text = []
	for chunk_id in i[0]:
		try:
			cid = int(chunk_id)
   
		except Exception:
			continue

		if cid == -1:
			continue

		chunk_content = await files_repo.select_chunk_text(cid,conn)
  
		if chunk_content:
			chunks_text.append(chunk_content)
   
	return groq_infra.chat_response(chunks_text,question,system_prompt)



async def delete_file(file_id: int, uid: str, conn):
	owner_id = await files_repo.get_owner_id(uid, conn)
 
	deleted_id = await files_repo.delete_file(file_id,owner_id,conn)
 
	if deleted_id is None:
		return {"msg": f"file with id {file_id} not found or is not yours"}

	await conn.commit()
 
	faiss_path = Path(f"data/users/user_{owner_id}/index_faiss_{file_id}.faiss")
	if faiss_path.exists():
		os.remove(faiss_path)
  
	else:
		print(f"got trouble deleting faiss index with owner id {owner_id} and id file id {file_id}, path doesn't exist")

	return {"msg": f"file with id {deleted_id} has been deleted"}
