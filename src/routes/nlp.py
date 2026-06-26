from fastapi import FastAPI, Depends, APIRouter, UploadFile, status, Request
from fastapi.responses import JSONResponse
from helpers.config import Settings, get_settings
from models import ResponseEnums, AssetsEnum
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from .schemas.nlp import PushRequest, SearchRequest, GenerateRequest
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
    
    nlp_controller = request.state.nlp_controller
    chunk_model = await ChunkModel.create_instance(db_client=request.state.Database)
    should_reset = str(push_request.do_reset).strip().lower() in ['1', 'true', 'yes']
    if should_reset:
        nlp_controller.reset_collection(project.project_id)
        logger.info(f"Collection for project {project_id} has been reset successfully.")
    import time
    time.sleep(3)
    page_no = 1
    actual_inserted = 0
    has_more_chunks = True
    while has_more_chunks:
        chunks, total_pages = await chunk_model.get_chunks_related_to_project(project_id=str(project.id), page_no=page_no)
        if not chunks:
            has_more_chunks = False
            break
        page_no += 1
        actual_inserted += len(chunks)
        is_inserted = nlp_controller.index_into_vector_db(
            project=project,
            chunks=chunks,
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
            "inserted_chunks": actual_inserted
        }
    )
    
@nlp_router.get("/collections")
async def get_collections(request:Request):
    nlp_controller = request.state.nlp_controller
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
    nlp_controller = request.state.nlp_controller

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
    embedding_client = request.state.embedding_client
    nlp_controller = request.state.nlp_controller
    
    query_vector = embedding_client.embed_text(text=request_data.query_text, doc_type=request_data.doc_type)
    
  
    search_results = nlp_controller.search_vectors(
        project_id=project_id,
        query_vector=query_vector,
        filters=request_data.filters,
        top_k=request_data.top_k,
        query_text= request_data.query_text
    )
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "success",
            "results": search_results
        }
    )
    

@nlp_router.post("/generate/{project_id}")
def generate_text(project_id: str, request_data: GenerateRequest, request: Request):
    
    nlp_controller = request.state.nlp_controller
    query = request_data.query 
    if not query:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "message": "Prompt text is required for generation."
            }
        )
    prompt_structured = nlp_controller.build_rag_prompt(
        query=query,
        project_id = project_id,
    )
    logger.info(prompt_structured)
    generated_text = nlp_controller.generate_text(
        prompt=prompt_structured,
        temperature=request_data.temperature,
        max_tokens=request_data.max_tokens
    )
    
    if generated_text is None:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": ResponseEnums.GenerationFailedERROR.value,
                "message": "Text generation failed."
            }
        )
    return JSONResponse(
    status_code=status.HTTP_200_OK,
    content={
        "answer": generated_text,
        "sources": []
    }
)
    
@nlp_router.get("/rest_collections/{project_id}")
def rest_collections(project_id, request: Request):
    nlp_controller = request.state.nlp_controller
    _ = nlp_controller.reset_collection(project_id)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "success",
        }
    )