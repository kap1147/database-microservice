from pydantic import BaseModel, Field
from fastapi import UploadFile
from uuid import UUID

class RahBase(BaseModel):
    class Config:
        orm_mode = True

class Image(RahBase):    
    filename: str
    user_id: UUID  
    day_or_night: bool
    overview_or_details: bool
    position: int = Field(le=10)
