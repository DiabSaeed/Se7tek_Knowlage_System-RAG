from .BaseDataModel import BaseDataModel
from .db_schema.chunk import ChunkSchema
from .enums.ProjectEnums import ProjectEnum
from bson.objectid import ObjectId
from pymongo import InsertOne

class ChunkModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = db_client[ProjectEnum.COLLECTION_CHUNKS_NAME.value]
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collections_and_indexes()
        return instance
    async def init_collections_and_indexes(self):
        collections = await self.db_client.list_collection_names()
        if ProjectEnum.COLLECTION_CHUNKS_NAME.value not in collections:
            self.collection = self.db_client[ProjectEnum.COLLECTION_CHUNKS_NAME.value]
            indexes = ChunkSchema.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index['key'],
                    name=index['name'],
                    unique=index['unique']
                )
    async def insert_new_chunk(self, chunk: ChunkSchema):
        
        result = await self.collection.insert_one(chunk.model_dump(by_alias=True,exclude_unset=True))
        chunk.id = result.inserted_id
        return chunk
    async def get_chunks_related_to_project(self,project_id: str, page_no: int = 1, page_size:int = 10):
        
        total_chunks = await self.collection.count_documents({"chunk_project_id" : ObjectId(project_id) if isinstance(project_id,str) else project_id})
        total_pages = total_chunks // page_size
        if total_pages % page_size > 0: 
            total_pages +=1
        cursor = self.collection.find().skip((page_no-1) * page_size).limit(page_size)
        docs = []
        
        async for doc in cursor:
            docs.append(
                ChunkSchema(**doc)
            )
        return docs, total_pages
    async def get_chunk(self,chunk_id:str):
        record = await self.collection.find_one({"_id": ObjectId(chunk_id)})
        if record:
            return ChunkSchema(**record)
        else:
            return None
    async def insert_many_chunks(self, chunks: list, batch_size: int = 100 ):
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i: i + batch_size]
            
            operation = [
                InsertOne(chunk.model_dump(by_alias=True,exclude_unset=True))
                for chunk in batch
            ]
            
            await self.collection.bulk_write(operation)
        return len(chunks)
    async def delete_chunks_related_to_project(self, project_id: ObjectId):
        
            result = await self.collection.delete_many({"chunk_project_id": project_id})
            return result.deleted_count
            