from .BaseController import BaseController
from .ProjectController import ProjectController
from fastapi import UploadFile
from models.enums import ResponseEnums
import os
import re
import hashlib

class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.mb = 1048576
    def validate_file(self,file:UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseEnums.FILE_TYPE_NOT_SUPPORTED
        if file.size and file.size > self.app_settings.FILE_MAX_SIZE * self.mb:
            return False, ResponseEnums.FILE_SIZE_EXCEEDED
        
        return True, ResponseEnums.FILE_UPLOADED_SUCCEEDED
    def generate_unique_filename(self,file_name:str, project_id: str):
        unique_part = hashlib.md5(
        f"{file_name}{project_id}".encode()
        ).hexdigest()
        project_path = ProjectController().create_project_path(project_id=project_id)
        cleaned_file_name = self.get_file_name_cleaned(file_name=file_name)
        project_path = os.path.join(
            project_path,
            str(unique_part) + "_" + cleaned_file_name
        )
        file_id = str(unique_part) + "_" + cleaned_file_name
        return project_path, file_id
    
    def get_file_name_cleaned(self,file_name:str):
        name, ext = os.path.splitext(file_name)

        clean_name = re.sub(r'[^\w]', '', name)

        cleaned_file_name = f"{clean_name}{ext}"

        cleaned_file_name = cleaned_file_name.replace(" ","_")
        return cleaned_file_name