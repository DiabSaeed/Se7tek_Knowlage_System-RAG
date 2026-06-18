from .Provider import QdrandDB
from .Enums.VectorEnums import QdrantEnums
from ...helpers.config import Settings
from ...controllers.BaseController import BaseController

import logging

class VectorFactory:
    def __init__(self, congig):
        self.config = Settings() #type: ignore
        self.path = BaseController()
    def create(self, provider):
        if provider == QdrantEnums.DBName.value:
            db_complete_path = self.path.get_database_path(db_name= self.config.VECTOR_DB_PATH)
            QdrandDB(
                db_path=db_complete_path ,
                distance_mode=self.config.VECTOR_DB_DIStANCE
            )
        raise ValueError(f"Unsupported Vector DB backend: {provider}")