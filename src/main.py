from fastapi import FastAPI
from routes import base, data, nlp
from contextlib import asynccontextmanager
from motor import motor_asyncio
from helpers.config import Settings
from stores.llms import LlmFactory
from stores.VectorDB import VectorFactory

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings() #type: ignore
    connection = motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
    client = connection[settings.MONGODB_NAME]
    
    # LLM Provider Factory 
    llm_provide_factory = LlmFactory(settings)
    
    generation_client = llm_provide_factory.create_provider(settings.GENERATION_BACKEND)
    generation_client.set_generation_model(model_id= settings.GENERATION_MODEL_ID) #type: ignore
    embedding_client = llm_provide_factory.create_provider(settings.EMBEDING_BACKEND)
    embedding_client.set_embedding_model(model_id= settings.EMBEDING_MODEL_ID , embeding_size= settings.EMBEDING_MODEL_SIZE) #type: ignore
    
    # Vector Provider Factory 
    vector_provide_factory = VectorFactory(settings)
    
    qdrant_db = vector_provide_factory.create(settings.VECTOR_DB_BACKEND)
    qdrant_db.connect()
    
    yield {
        "connection": connection,
        "Database": client,
        "generation_client": generation_client,
        "embedding_client" : embedding_client,
        "vector_db": qdrant_db
           }
    connection.close()
    
app = FastAPI(lifespan=lifespan)
app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)