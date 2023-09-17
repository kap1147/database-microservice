from pydantic import BaseModel, Field
from dataclasses import dataclass, field 
from fastapi import UploadFile
from uuid import UUID

class RahBase(BaseModel):
    class Config:
        orm_mode = True

class ImagePost(RahBase):    
    filename: str
    user_id: UUID  
    system_name: str
    prop_type: str
    position: int = Field(le=10)


@dataclass
class ImageGet:
    user_id: UUID
    system_name: str
    prop_type: str
    position: int
