from .BaseController import BaseController
import os


class ProjectController(BaseController):
    def __init__(self):
        super().__init__()

    def create_project_path(self, project_id: str):
        file_path = os.path.join(self.files_path, project_id)
        os.makedirs(file_path, exist_ok=True)
        return file_path