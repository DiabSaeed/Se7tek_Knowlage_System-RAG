from fastapi import FastAPI, Depends, APIRouter, UploadFile, status
from fastapi.responses import JSONResponse
from helpers.config import Settings, get_settings
from controllers import DataController, ProjectController, ProcessControler,ChunckingController
from .schemas.data import ProcessRequest
import os 
import aiofiles
from models import ResponseEnums
import logging

logger = logging.getLogger('uvicorn.error')
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api/v1","data"]
)

@data_router.post("/upload/{project_id}")
async def upload_files(project_id: str,
                       file: UploadFile,
                       app_settings: Settings=Depends(get_settings)):
    data_controller = DataController()
    is_valid,message = data_controller.validate_file(file=file)

    if not is_valid:
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content={
                "signal": is_valid,
                "message":message.value
            }
        )

    file_path,file_id = data_controller.generate_unique_filename(file_name=file.filename or "unnamed_file.pdf",project_id=project_id)
    try: 
        async with aiofiles.open(file_path,"wb") as f:
            while chunk := await file.read(app_settings.FILE_CHUNCK_SIZE):
                await f.write(chunk)
            
        return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "signal": ResponseEnums.FILE_UPLOADED_SUCCEEDED.value,
                    "file_id": file_id
                }
            )
    
    except Exception as e:
        logger.error(f"Error while uploading file as {e}")
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseEnums.FILE_UPLOADED_FIELD.value,
                }
            )
@data_router.post("/process/{project_id}")
async def process_file(
    project_id: str,
    process_request: ProcessRequest
):
    file_id = process_request.file_id
    file_path = ProjectController().create_project_path(project_id=project_id)+"/"+file_id+".pdf"
    chunk_size = process_request.chunk_size
    chunk_overlab = process_request.chunk_overlab
    process_controller = ProcessControler(project_id=project_id)
    file_content = process_controller.content_transformation(file_path=file_path)
    chunking = ChunckingController(chunk_size=chunk_size,recursive_chars=chunk_overlab)
    file_chuncks = chunking.chunk_splitter(file_content)
    if file_chuncks is None or len(file_chuncks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": "Failed"
            }
        )
    return file_chuncks