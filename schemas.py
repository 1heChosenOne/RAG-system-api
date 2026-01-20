from pydantic import BaseModel, Field, EmailStr

class FileQuestion(BaseModel):
    file_id:int
    question:str = Field(...,max_length=500)
    
class PassEmail(BaseModel):
    email: EmailStr
    password:str = Field(...,min_length=4,max_length=16)
    