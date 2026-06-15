from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime

class AssetSchema (BaseModel):
    id : Optional[ObjectId] = Field(default_factory=ObjectId,alias='_id')
    asset_name : str = Field(...,min_length=1)
    asset_project_id: Optional[ObjectId]
    asset_size: int = Field(gt=1)
    asset_type: str = Field(...,min_length=1)
    asset_config: dict = Field(default={})
    asset_pused_at: datetime = Field(default=datetime.now())
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [
                    ("asset_project_id",1)
                ],
                "name":"asset_project_id_index_1",
                "unique":False
            },
            {
                "key": [
                    ("asset_name",1)
                ],
                "name":"asset_name_index_1",
                "unique":False
            },
            {
                "key": [
                    ("asset_project_id",1),
                    ("asset_name",1)
                ],
                "name":"asset_project_id_composed_index_1",
                "unique":True
            }
            
        ]