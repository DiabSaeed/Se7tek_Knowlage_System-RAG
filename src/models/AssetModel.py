from .BaseDataModel import BaseDataModel
from .db_schema.assets import AssetSchema
from .enums.ProjectEnums import ProjectEnum
from bson.objectid import ObjectId

class AssetModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client = db_client)
        self.collection = self.db_client[ProjectEnum.COLLECTION_ASSET_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collections_and_indexes()
        return instance
    


    async def init_collections_and_indexes(self):
        collections = await self.db_client.list_collection_names()
        if ProjectEnum.COLLECTION_ASSET_NAME.value not in collections:
            self.collection = self.db_client[ProjectEnum.COLLECTION_ASSET_NAME.value]
            indexes = AssetSchema.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index['key'],
                    name=index['name'],
                    unique=index['unique']
                )
    
    async def create_asset(self,asset:AssetSchema):
        result = await self.collection.insert_one(asset.model_dump(by_alias=True,exclude_unset=True))
        asset.id = result.inserted_id
        return asset
    async def get_chunks_related_to_project(self,project_id: str):
        
        total_assets = await self.collection.find(
            {"asset_project_id": ObjectId(project_id) if isinstance(project_id, str) else project_id}
        ).to_list(length=None)
        
        return total_assets