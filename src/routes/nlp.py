from fastapi import FastAPI, Depends, APIRouter, UploadFile, status, Request
from fastapi.responses import JSONResponse
from helpers.config import Settings, get_settings
from models import ResponseEnums, AssetsEnum
from models.ProjectModel import ProjectModel
from .schemas.nlp import PushRequest
from ..controllers.NlpController import NlpController
import logging

logger = logging.getLogger('uvicorn.error')
nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api/v1","nlp"]
)

@nlp_router.post("/index/push/{project_id}")
async def push_index(project_id: str,
                     request:Request,
                     app_settings: Settings=Depends(get_settings),
                     push_request: PushRequest = Depends()):
    
    project_model = await ProjectModel.create_instance(
        db_client= request.state.Database
    )
    project = await project_model.get_project_or_create(
        project_id=project_id
        )
    
    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": ResponseEnums.ProjectNotfoundERROR.value,
                "message": f"Project with ID {project_id} not found."
            }
        )
    
    vector_client = request.state.vector_db
    embedding_client = request.state.embedding_client
    generation_client = request.state.generation_client
    nlp_controller = NlpController(
        vector_client=vector_client,
        embedding_client= embedding_client,
        generation_client=generation_client
    )
    