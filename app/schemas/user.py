from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    userId: int
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"