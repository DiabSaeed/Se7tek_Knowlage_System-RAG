from fastapi import FastAPI, Depends, APIRouter, UploadFile, status, Request
from fastapi.responses import JSONResponse
from helpers.config import Settings, get_settings
from controllers import DataController, ProjectController, ProcessControler,ChunckingController
from .schemas.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.db_schema.chunk import ChunkSchema
from models.db_schema.assets import AssetSchema
from models.AssetModel import AssetModel
from bson import ObjectId
import os 
import aiofiles
from models import ResponseEnums, AssetsEnum
import logging

logger = logging.getLogger('uvicorn.error')
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api/v1","data"]
)

@data_router.post("/upload/{project_id}")
async def upload_files(project_id: str,
                       file: UploadFile,
                       request:Request,
                       app_settings: Settings=Depends(get_settings)):
    project_model = await ProjectModel.create_instance(
        db_client= request.state.Database
    )
    project = await project_model.get_project_or_create(
        project_id=project_id
        )
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
            
        # storing file metadata into the mongo collection (Assets)
        
        asset_model = await AssetModel.create_instance(
            db_client= request.state.Database
        )
        existing = await asset_model.get_asset(
            project_id=project.id,
            asset_name=file_id
        )

        if existing:
            return JSONResponse(
                status_code=409,
                content={
                    "message": "File already exists"
                }
            )
        asset_schema = AssetSchema(
            asset_project_id= project.id,
            asset_name= file_id,
            asset_size= os.path.getsize(file_path),
            asset_type=AssetsEnum.FILE.value
        )
        asset_record = await asset_model.create_asset(asset=asset_schema)
        return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "signal": ResponseEnums.FILE_UPLOADED_SUCCEEDED.value,
                    "file_id": str(asset_record.id)
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
        process_request: ProcessRequest,
        request: Request
    ):
    
    chunk_model = await ChunkModel.create_instance(db_client=request.state.Database)
    project_model = await ProjectModel.create_instance(db_client=request.state.Database)
    assets_model = await AssetModel.create_instance(db_client=request.state.Database)
    
    do_reset = process_request.do_reset
    files_to_process = []
    project = await project_model.get_project_or_create(project_id=project_id)
    
    if do_reset == 1:
        if project.id:
            _ = await chunk_model.delete_chunks_related_to_project(project_id=project.id)
            
    if process_request.file_id is not None:
        files_to_process = [process_request.file_id]
    else:
        files_to_process = [
            file['asset_name']
            for file in await assets_model.get_chunks_related_to_project(project_id=str(project.id))
        ]
        
    total_chunks = 0
    processed_files = 0
    
    for file_id in files_to_process:
        base_path = ProjectController().create_project_path(project_id=project_id)
        file_path = os.path.join(base_path, f"{file_id}{'.pdf' if '.pdf' not in file_id else ''}")
        chunk_size = process_request.chunk_size if process_request.chunk_size else 1000
        chunk_overlab = process_request.chunk_overlab if process_request.chunk_overlab else 200
        process_controller = ProcessControler(project_id=project_id)
        
        file_content = await process_controller.content_transformation(file_path=file_path)
        chunking = ChunckingController(chunk_size=chunk_size)
        file_chunks = chunking.chunk_splitter(file_content)
        
        if file_chunks is None or len(file_chunks) == 0:
            logger.error(f"error while handling file {file_id}")
            continue
            
        chunks = [
            ChunkSchema(
            chunk_order = i+1,
            metadata = c.metadata,
            page_content = c.page_content,
            type = c.type,
            chunk_project_id = project.id)
            for i, c in enumerate(file_chunks)] 
        
        total_chunks += await chunk_model.insert_many_chunks(chunks)
        processed_files += 1
        
    return JSONResponse({
        "signal": ResponseEnums.PROCESS_STARTED_SUCCE.value,
        "Number of chuncks": total_chunks,
        "Number of Processed Files": processed_files
    })