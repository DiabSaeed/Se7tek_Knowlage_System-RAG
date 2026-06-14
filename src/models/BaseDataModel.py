from helpers.config import Settings

class BaseDataModel:
    def __init__(self, db_client):
        self.db_client = db_client
        self.app_settings = Settings()
        