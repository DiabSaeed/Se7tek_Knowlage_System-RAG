from fastapi import FastAPI
from routes import base, data, nlp
from contextlib import asynccontextmanager
from motor import motor_asyncio
from helpers.config import Settings
from stores.llms import LlmFactory
from stores.VectorDB import VectorFactory
from stores.llms.templates import PromptParser
from controllers.NlpController import NlpController
from stores.llms.GenerationInterface import GenerationInterface
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN") or ""
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1" 

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
    
    # Template Parser
    prompt_parser = PromptParser(locale=settings.DEFAULT_LANGUAGE)
    
    if not embedding_client:
        raise ValueError("Failed to initialize Embedding Client. Check your Factory config.")
    if not generation_client:
        raise ValueError("Failed to initialize Generation Client. Check your Factory config.")
    if not qdrant_db:
        raise ValueError("Failed to initialize Vector DB. Check your Factory config.")
    if not isinstance(generation_client, GenerationInterface):
        raise TypeError("Generation client does not implement GenerationInterface")
    # NlpController
    nlp_controller = NlpController(
        vector_client=qdrant_db,
        embedding_client= embedding_client,
        generation_client=generation_client,
        prompt_parser=prompt_parser
    )
    
    yield {
        "connection": connection,
        "Database": client,
        "generation_client": generation_client,
        "embedding_client" : embedding_client,
        "vector_db": qdrant_db,
        "prompt_parser": prompt_parser,
        "nlp_controller": nlp_controller
           }
    connection.close()
    
app = FastAPI(lifespan=lifespan)
app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)