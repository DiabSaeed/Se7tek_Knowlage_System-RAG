from fastapi import FastAPI
from routes import base, data
from contextlib import asynccontextmanager
from motor import motor_asyncio
from helpers.config import Settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()
    connection = motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
    client = connection[settings.MONGODB_NAME]
    yield {
        "connection": connection,
        "Database": client
           }
    connection.close()



app = FastAPI(lifespan=lifespan)
app.include_router(base.base_router)
app.include_router(data.data_router)