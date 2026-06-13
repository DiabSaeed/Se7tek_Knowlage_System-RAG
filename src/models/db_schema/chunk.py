from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId

class ChunkSchema (BaseModel):
    _id : Optional[ObjectId]
    metadata: dict
    page_content : str = Field(...,min_length=1)
    type : str 
    chunk_project_id: ObjectId
    class Config:
        arbitrary_types_allowed = True