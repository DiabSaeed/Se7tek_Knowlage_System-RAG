from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId

class ProjectSchema (BaseModel):
    _id : Optional[ObjectId]
    project_id: str
    file_id : str = Field(...,min_length=1)
    
    @field_validator('project_id')
    def validate_project_id(cls,value: str):
        if not value.isalnum():
            raise ValueError("Project_id must be number")
        return value
    class Config:
        arbitrary_types_allowed = True