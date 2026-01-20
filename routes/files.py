from fastapi import APIRouter, Depends, Response, UploadFile
from utils import auth, check_current_token, config
from db import get_conn
from services.auth import get_hashed_pass_from_db, sign_up
from services.profile import addfile, all_files, delete_file, chat
from schemas import PassEmail, FileQuestion

router = APIRouter()


@router.get("/my_files")
async def all_files_r(current_user: str = Depends(check_current_token),uid: str = auth.CURRENT_SUBJECT, conn=Depends(get_conn)):
    return await all_files(uid,conn)


@router.post("/sign_up")
async def sign_up_r(body:PassEmail,conn=Depends(get_conn)):
    return await sign_up(body.email,body.password,conn)


@router.post("/log_in")
async def log_in_r(body:PassEmail, response: Response, conn=Depends(get_conn)):
    token = await get_hashed_pass_from_db(body.password, body.email, conn)
    
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
    return {"msg":"succesful log in, token has been added to your cookies"}



@router.post("/addfile")
async def addfile_r(file: UploadFile, current_user: str = Depends(check_current_token), conn=Depends(get_conn), uid: str = auth.CURRENT_SUBJECT):
    return await addfile(file, uid, conn)


@router.delete("/delete_file")
async def delete_file_r(file_id: int, current_user: str = Depends(check_current_token), uid: str = auth.CURRENT_SUBJECT, conn=Depends(get_conn)):
    return await delete_file(file_id, uid, conn)


@router.post("/chat")
async def chat_r(body:FileQuestion, current_user: str = Depends(check_current_token), uid: str = auth.CURRENT_SUBJECT, conn=Depends(get_conn)):
    return await chat(body.question, body.file_id, uid, conn)