from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId

class ChunkSchema (BaseModel):
    id : Optional[ObjectId] = Field(default_factory=ObjectId,alias='_id')
    chunk_order : int
    metadata: dict
    page_content : str = Field(...,min_length=1)
    type : str 
    chunk_project_id: Optional[ObjectId]
    class Config:
        arbitrary_types_allowed = True
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [
                    ("chunk_project_id",1)
                ],
                "name":"chunk_project_id_index_1",
                "unique":False
            }
        ]