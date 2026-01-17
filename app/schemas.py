from pydantic import BaseModel,Field 
from typing import Annotated

class UserCreate(BaseModel):
    username: str
    email: str
    password: Annotated[str, Field(..., min_length=8, max_length=72, description="password type")] 

class UserLogin(BaseModel):
    username: str
    password: str

class ServerCreate(BaseModel):
    name: str
    host: str
    username: str
    port: int = 22

class ServerResponse(ServerCreate):
    id: int

    class Config:
        from_attributes = True
    
class CommandRequest(BaseModel):
    command: str