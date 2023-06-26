from pydantic import BaseModel, Field
# from uuid import UUID

class RahBase(BaseModel):
    class Config:
        orm_mode = True

class Image(RahBase):    
    user_id: str
    position: int = Field(le=9)
    binary: bytes
