from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId
from uuid import UUID
class ProjectSchema (BaseModel):
    id : Optional[ObjectId] = Field(default_factory=ObjectId,alias='_id')
    project_id: str
    file_id : str = Field(min_length=1,default="1") 
    
    class Config:
        arbitrary_types_allowed = True
        
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [
                    ("project_id",1)
                ],
                "name":"project_id_index_1",
                "unique":True
            }
        ]