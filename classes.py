from pydantic import BaseModel, Field, EmailStr

class file_and_question(BaseModel):
    file_id:int
    question:str = Field(...,max_length=500)
    
class pass_and_email(BaseModel):
    email: EmailStr
    password:str = Field(...,min_length=4,max_length=16)
    