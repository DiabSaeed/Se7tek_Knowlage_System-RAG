from helpers.config import Settings, get_settings
import os
class BaseController:
    def __init__(self):
        self.app_settings = get_settings()
        self.project_path = os.path.dirname(os.path.dirname(__file__))
        self.files_path = os.path.join(
            self.project_path,
            "assets",
            "files"
        )
        self.db_path = self.files_path = os.path.join(
            self.project_path,
            "assets",
            "databases"
        )
    def get_database_path(self, db_name):
        db_Complete_path =  os.path.join(
            self.db_path,
            db_name
        )
        if not db_Complete_path:
            os.mkdir(db_Complete_path)
        
        return db_Complete_path