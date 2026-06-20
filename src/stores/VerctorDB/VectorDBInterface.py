from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from qdrant_client.models import Filter
class VectorDBInterface(ABC):
    
    @abstractmethod
    def connect(self):
        pass
    
    @abstractmethod
    def disconnect(self):
        pass
    
    @abstractmethod
    def is_collection_exists(self, collection_name: str) -> bool:
        pass
    
    @abstractmethod
    def create_collection(self, collection_name:str, embedding_size: int = 1024):
        pass
    
    @abstractmethod
    def get_all_collections(self) -> List[str]:
        pass
    
    @abstractmethod
    def insert_one_vector(self, vector: List[float], text:str, collection_name: str, metadata: str, id : str, embedding_size: int) -> bool:
        pass
    
    @abstractmethod
    def insert_many(self, vectors: List[List[float]],
                    texts:List[str],
                    collection_name: str,
                    metadatas: list,
                    ids : list,
                    embedding_sizes: list,
                    batch_size:int = 64,
                    parallel: int = 2)-> bool:
        pass
    
    @abstractmethod
    def search(self, collection_name: str, query_vector: List[float], top_k: int = 5,filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def delete(self, collection_name: str, ids: Optional[List]) -> bool:
        pass
    
    @abstractmethod
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def delete_collection(self, collection_name: str) -> bool:
        pass
    