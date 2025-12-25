from authx import AuthX, AuthXConfig 
import bcrypt
from sqlalchemy import text
from fastapi import HTTPException, Request
import re
from pathlib import Path
from dotenv import load_dotenv
import os
from groq import Groq



load_dotenv()
groq_api_key=os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=groq_api_key)
jwt_secret_key=os.getenv("JWT_SECRET_KEY")

config=AuthXConfig(JWT_ACCESS_TOKEN_EXPIRES= 60 * 60)#can be changed for your preferences
config.JWT_SECRET_KEY=jwt_secret_key
config.JWT_ACCESS_COOKIE_NAME="my_access_token"
config.JWT_TOKEN_LOCATION=["cookies"]
config.JWT_COOKIE_CSRF_PROTECT = False
auth = AuthX(config=config)
auth.set_callback_get_model_instance(lambda subject,**kwargs:subject)



BASE_PATH = Path("data/users")

def password_in_hash(password:str):
    salt=bcrypt.gensalt()
    hashed=bcrypt.hashpw(password.encode(),salt)
    return hashed.decode()

def verify_hash(password: str, hashed: str):
    return bcrypt.checkpw(password.encode(), hashed.encode())

async def get_owner_id(email,conn):
    res=await conn.execute(text("""SELECT id FROM users WHERE email=:email"""),{"email":email})
    owner_id=res.scalar_one_or_none()
    return owner_id
    
async def check_current_token(request: Request):
    try:
        return await auth.access_token_required(request)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Token expired or invalid")
    
def validate_filename(name: str) -> str:
    if not re.match(r"^[\w\-.]{1,255}$", name):
        raise HTTPException(400, "Invalid filename")
    return name

def get_user_dir(user_id: str) -> Path:
    path = BASE_PATH / f"user_{user_id}"
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_file_dir(user_id: str, file_id: str) -> Path:
    path = get_user_dir(user_id) / f"file_{file_id}"
    path.mkdir(parents=True, exist_ok=True)
    return path