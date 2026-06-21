from fastapi import FastAPI, Depends, APIRouter, UploadFile, status, Request
from fastapi.responses import JSONResponse
from helpers.config import Settings, get_settings
from models import ResponseEnums, AssetsEnum
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from .schemas.nlp import PushRequest, SearchRequest
from controllers.NlpController import NlpController
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
    chunk_model = await ChunkModel.create_instance(db_client=request.state.Database)
    
    page_no = 1
    has_more_chunks = True
    while has_more_chunks:
        chunks, total_pages = await chunk_model.get_chunks_related_to_project(project_id=str(project.id), page_no=page_no)
        if not chunks:
            has_more_chunks = False
            break
        page_no += 1
        
        is_inserted = nlp_controller.index_into_vector_db(
            project=project,
            chunks=chunks,
            do_reset=bool(push_request.do_reset)
        )
        
        if not is_inserted:
            logger.error(f"Failed to index chunks for project {project_id} at page {page_no}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "status": ResponseEnums.IndexingFailedERROR.value,
                    "message": f"Failed to index chunks for project {project_id} at page {page_no}"
                }
            )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": ResponseEnums.PROCESS_STARTED_SUCCE.value,
            "message": f"Indexing process for project {project_id} has been started successfully.",
            "inserted_chunks": int(page_no) * int(push_request.page_size)
        }
    )
    
@nlp_router.get("/collections")
async def get_collections(request:Request):
    vector_client = request.state.vector_db
    nlp_controller = NlpController(
        vector_client=vector_client,
        embedding_client= request.state.embedding_client,
        generation_client=request.state.generation_client
    )
    collections = nlp_controller.get_all_collections()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "success",
            "collections": collections
        }
    )

@nlp_router.get("/collections/{project_id}")
async def get_collection_info(project_id: str, request:Request):
    vector_client = request.state.vector_db
    nlp_controller = NlpController(
        vector_client=vector_client,
        embedding_client= request.state.embedding_client,
        generation_client=request.state.generation_client
    )
    project_model = await ProjectModel.create_instance(
        db_client= request.state.Database
    )
    project = await project_model.get_project_or_create(project_id=project_id)
    collection_info = nlp_controller.get_collection_info(project_id= project_id)
    if not collection_info:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": ResponseEnums.CollectionNotFoundERROR.value,
                "message": f"Collection for project {project_id} not found."
            }
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "success",
            "collection_info": collection_info
        }
    )

@nlp_router.post("/search/{project_id}")
def search_vectors(project_id: str, request_data: SearchRequest, request: Request):
    vector_client = request.state.vector_db
    embedding_client = request.state.embedding_client
    generation_client = request.state.generation_client
    
    nlp_controller = NlpController(
        vector_client=vector_client,
        embedding_client=embedding_client,
        generation_client=generation_client
    )
    
    query_vector = embedding_client.embed_text(text=request_data.query_text, doc_type=request_data.doc_type)
    
  
    search_results = nlp_controller.search_vectors(
        project_id=project_id,
        query_vector=query_vector,
        filters=request_data.filters,
        top_k=request_data.top_k
    )
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "success",
            "results": search_results
        }
    )
    
