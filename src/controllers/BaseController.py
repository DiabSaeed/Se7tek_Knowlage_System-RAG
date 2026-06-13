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