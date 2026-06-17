from fastapi import FastAPI
from routes import base, data
from contextlib import asynccontextmanager
from motor import motor_asyncio
from helpers.config import Settings
from .stores.llms.LlmProvideFactory import LlmFactory

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings() #type: ignore
    connection = motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
    client = connection[settings.MONGODB_NAME]
    
    # Provide Factory 
    llm_provide_factory = LlmFactory(settings)
    
    generation_client = llm_provide_factory.create_provider(settings.GENERATION_BACKEND)
    generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID) #type: ignore
    embedding_client = llm_provide_factory.create_provider(settings.EMBEDING_BACKEND)
    embedding_client.set_embedding_model(model_id= settings.EMBEDING_MODEL_ID , embeding_size= settings.EMBEDING_MODEL_SIZE) #type: ignore
    
    yield {
        "connection": connection,
        "Database": client,
        "generation_client": generation_client,
        "embedding_client" : embedding_client
           }
    connection.close()
    
app = FastAPI(lifespan=lifespan)
app.include_router(base.base_router)
app.include_router(data.data_router)