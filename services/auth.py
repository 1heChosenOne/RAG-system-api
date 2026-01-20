from utils import verify_hash, auth, password_in_hash
from repos import files as files_repo
from sqlalchemy.exc import IntegrityError
from exceptions import EmailNotFound, PassEmailIncorrect


async def get_hashed_pass_from_db(password, email, conn): # It also checks for exact similarity
    
    hashed_pass=await files_repo.select_pass_hash(email,conn)
    if not hashed_pass:
        raise EmailNotFound(email)
    
    if not verify_hash(password,hashed_pass):
        raise PassEmailIncorrect()
    
    token=auth.create_access_token(uid=email)
    return token



async def sign_up(email,password,conn):
    password_hash=password_in_hash(password)
    
    try:
        await files_repo.insert_user(email,password_hash,conn)

    except IntegrityError as e:
        if "unique constraint" in str(e.orig):
            return {"error": "Email is already taken"}
        
    await conn.commit()
    return {"msg":"Succesful registration"}


