from .BaseDataModel import BaseDataModel
from .db_schema.project import ProjectSchema
from .enums.ProjectEnums import ProjectEnum

class ProjectModel(BaseDataModel):
    
    def __init__(self, db_client: object):
        super().__init__(db_client = db_client)
        self.collection = self.db_client[ProjectEnum.COLLECTION_PROJECT_NAME.value]
        
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collections_and_indexes()
        return instance
    
    async def init_collections_and_indexes(self):
        collections = await self.db_client.list_collection_names()
        if ProjectEnum.COLLECTION_PROJECT_NAME.value not in collections:
            self.collection = self.db_client[ProjectEnum.COLLECTION_PROJECT_NAME.value]
            indexes = ProjectSchema.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index['key'],
                    name=index['name'],
                    unique=index['unique']
                )
                
    async def create_project(self,project: ProjectSchema):
        
        result = await self.collection.insert_one(project.model_dump(by_alias=True,exclude_unset=True))
        project.id = result.inserted_id
        
        return project
    
    async def get_project_or_create(self, project_id: str):
        record = await self.collection.find_one({
            "project_id" : project_id
        })
        if not record:
            project = ProjectSchema(project_id=project_id)
            project = await self.create_project(project=project)
            return project
        return ProjectSchema(**record)
    async def get_all_projects(self,page:int = 1 , page_size:int = 10):
        total_docs = await self.collection.count_documents({})
        total_pages = total_docs // page_size
        if total_pages % page_size > 0: 
            total_pages +=1
        cursor = self.collection.find().skip((page-1) * page_size).limit(page_size)
        docs = []
        
        async for doc in cursor:
            docs.append(
                ProjectSchema(**doc)
            )
        return docs, total_pages
    