from qdrant_client.models import Distance, PointStruct, PointIdsList, VectorParams, Filter, MatchValue, FieldCondition
from qdrant_client import QdrantClient
from ..VectorDBInterface import VectorDBInterface
from ..Enums.VectorEnums import DistanceEnums
from typing import cast, List,Dict, Any, Optional
import uuid
import logging

class QdrandDB(VectorDBInterface):
    def __init__(self, distance_mode: str, db_path: str):
        
        self.db_path = db_path
        self.client = None
        self.client = cast(QdrantClient,self.client)
        self.logger = logging.getLogger(__name__)
        moder_dis  = distance_mode.lower().strip()
        
        self.distance_mode : Distance
        
        if moder_dis == DistanceEnums.DOT.value:
            self.distance_mode = Distance.DOT
        elif moder_dis == DistanceEnums.COSINE.value: 
            self.distance_mode = Distance.COSINE
        else:
             self.distance_mode = Distance.COSINE
            
    def connect(self):
        self.client = QdrantClient(path=self.db_path)
    
    def disconnect(self):
        raise NotImplementedError
    
    def _conver_filter_dict_to_Filter(self, filters: Optional[Dict[str, Any]]):
        if not filters:
            return None
        filters = cast(Dict, filters)
        conditions = []
        for key, value in filters.items():
            conditions.append(
                FieldCondition(
                    key= key,
                    match=MatchValue(value= value)
                )
            )
        return Filter(must=conditions)
    
    def is_collection_exists(self, collection_name: str)-> bool:
        if self.client:
            return self.client.collection_exists(
                collection_name= collection_name
            )
        else: 
            self.logger.error("Ensure of the DB client")
            raise ValueError("Database client is not connected. Call connect() first.")
    
    def create_collection(self, collection_name:str, embedding_size:int = 1024):
        if self.client:
            if self.is_collection_exists(collection_name= collection_name):
                return self.logger.info("Collection is already exists")
            else:
                _ = self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=embedding_size,
                    distance= self.distance_mode
                )
            )
        else:
            self.logger.error("Ensure of the DB client")
            raise ValueError("Database client is not connected. Call connect() first.")
    
    def get_all_collections(self) -> List[str]:
        if self.client:
            collections = self.client.get_collections()
            collection_names = [collection.name for collection in collections.collections]
            return collection_names
        else:
            self.logger.error("Ensure of the DB client")
            raise ValueError("Database client is not connected. Call connect() first.")
    
    def insert_one_vector(self, vector: List[float], text:str, collection_name: str, metadata: str, id : str, embedding_size: int) -> bool:
        if not self.client:

            self.logger.error("Ensure of the DB client")

            raise ValueError("Database client is not connected. Call connect() first.")

        if not self.is_collection_exists(collection_name=collection_name):

            self.logger.error(f"There is no collection with this Name: {collection_name}")

            return False

        points = [
            PointStruct(
                vector=vector,
                payload={

                    "text": text,

                    "metadata": metadata,

                    "embedding_size": embedding_size
                },

                id=id

            )
        ]
        self.client.upsert(

            collection_name=collection_name,

            points=points

        )
        return True
    
    def insert_many(self, vectors: List[List[float]],
                    texts:List[str],
                    collection_name: str,
                    metadatas: list,
                    ids : list,
                    embedding_sizes: list,
                    batch_size:int = 64,
                    parallel: int = 2)-> bool:
        if not self.client:

            self.logger.error("Ensure of the DB client")

            raise ValueError("Database client is not connected. Call connect() first.")

        if not self.is_collection_exists(collection_name=collection_name):

            self.logger.error(f"There is no collection with this Name: {collection_name}")

            return False
        lengths = [len(vectors), len(texts), len(metadatas), len(ids), len(embedding_sizes)]
        if len(set(lengths)) > 1:
            self.logger.warning("Mismatched list lengths in bulk insert.")
            if len(ids) < len(vectors):
                difference = len(vectors) - len(ids)
                generated_ids = [str(uuid.uuid4()) for _ in range(difference)]
                ids.extend(generated_ids)
                self.logger.warning(f"Auto-generated {difference} missing IDs.")
        
        payloads = [{
            "metadata": metadata,
            "text": text,
            "embedding_size": embedding_size,
        } for metadata, text, embedding_size in zip(metadatas,texts,embedding_sizes) ]
        points = [
            PointStruct(
                vector= vector,
                payload= payload,
                id = id
            )
            for vector, payload, id in zip(vectors, payloads, ids)
        ]
        _ = self.client.upload_points(
            collection_name= collection_name,
            points= points,
            batch_size= batch_size,
            parallel= parallel
            
        )
        return True
    
    def search(self, collection_name: str, query_vector: List[float], top_k: int = 5,filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if not self.client:

            self.logger.error("Ensure of the DB client")

            raise ValueError("Database client is not connected. Call connect() first.")

        if not self.is_collection_exists(collection_name=collection_name):

            self.logger.error(f"There is no collection with this Name: {collection_name}")

            return []
        qadrant_filters = self._conver_filter_dict_to_Filter(filters=filters)
        search_results = self.client.query_points(
            collection_name= collection_name,
            query= query_vector,
            limit= top_k,
            with_payload= True,
            with_vectors= False,
            query_filter= qadrant_filters
        )
        formatted_results = []
        for hit in search_results.points:
            payload = hit.payload or {} 
            
            formatted_results.append({
                "id": hit.id,
                "score": hit.score,
                "text": payload.get("text", ""),
                "metadata": payload.get("metadata", ""),
                "embedding_size": payload.get("embedding_size", 0)
            })

        return formatted_results
    
    def delete(self, collection_name: str, ids: Optional[List]) -> bool:
        if not self.client:

            self.logger.error("Ensure of the DB client")

            raise ValueError("Database client is not connected. Call connect() first.")

        if not self.is_collection_exists(collection_name=collection_name):

            self.logger.error(f"There is no collection with this Name: {collection_name}")

            return False
        if not ids:
            self.logger.warning("Delete called with an empty list of IDs.")
            return False
        if not self.is_collection_exists(collection_name=collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return False
        _ = self.client.delete(
            collection_name=collection_name,
            points_selector=PointIdsList(
                points=ids
            )
        )
        self.logger.info(f"Successfully deleted {len(ids)} points from {collection_name}")
        return True
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        if not self.client:
            self.logger.error("Ensure of the DB client")
            raise ValueError("Database client is not connected. Call connect() first.")

        if not self.is_collection_exists(collection_name=collection_name):
            self.logger.error(f"There is no collection with this Name: {collection_name}")
            return {}

        collection_info = self.client.get_collection(collection_name=collection_name)
        return collection_info.dict() if collection_info else {}
    
    def delete_collection(self, collection_name: str) -> bool:
        if not self.client:
            self.logger.error("Ensure of the DB client")
            raise ValueError("Database client is not connected. Call connect() first.")

        if not self.is_collection_exists(collection_name=collection_name):
            self.logger.error(f"There is no collection with this Name: {collection_name}")
            return False

        self.client.delete_collection(collection_name=collection_name)
        self.logger.info(f"Successfully deleted collection {collection_name}")
        return True