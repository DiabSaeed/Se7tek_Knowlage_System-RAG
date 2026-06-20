from .BaseController import BaseController
from ..stores.VerctorDB.Provider.QdranDB import QdrandDB
from ..stores.llms.Providers.GeneralProviders.OpenAIProvider import OpenaiProvider
from ..stores.llms.Providers.EmbeddingProviders.BGEM3Provider import BGEM3Provider
from ..models.db_schema import ProjectSchema, ChunkSchema
from typing import List, Optional, Dict, Any
import logging

class NlpController(BaseController):
    def __init__(self, vector_client: QdrandDB, embedding_client: BGEM3Provider, generation_client: OpenaiProvider):
        super().__init__()
        self.vector_client = vector_client
        self.embedding_client = embedding_client
        self.generation_client = generation_client
        self.logger = logging.getLogger(__name__)
    
    def create_collection_name (self, project_id: str) -> str:
        return f"collection_{project_id}"
    
    # VectorDB Operations
    def reset_collection(self, project_id: str) -> bool:
        collection_name = self.create_collection_name(project_id)
        if self.vector_client.is_collection_exists(collection_name):
            self.vector_client.delete_collection(collection_name=collection_name)
            return True
        else:
            self.logger.warning(f"Collection {collection_name} does not exist.")
            return False
        
    def create_collection(self, project_id: str, embedding_size: int = 1024) -> bool:
        collection_name = self.create_collection_name(project_id)
        if not self.vector_client.is_collection_exists(collection_name):
            self.vector_client.create_collection(collection_name=collection_name, embedding_size=embedding_size)
            return True
        else:
            self.logger.warning(f"Collection {collection_name} already exists.")
            return False
    
    def insert_vector(self, project_id: str, vector: list, text: str, metadata: str, id: str, embedding_size: int) -> bool:
        collection_name = self.create_collection_name(project_id)
        if not self.vector_client.is_collection_exists(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return False
        return self.vector_client.insert_one_vector(vector=vector, text=text, collection_name=collection_name, metadata=metadata, id=id, embedding_size=embedding_size)
    
    def insert_vectors(self, project_id: str, vectors: List[list], texts: List[str], metadatas: List[str], ids: List[str], embedding_sizes: List[int], batch_size: int = 64, parallel: int = 2) -> bool:
        collection_name = self.create_collection_name(project_id)
        if not self.vector_client.is_collection_exists(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return False
        return self.vector_client.insert_many(vectors=vectors, texts=texts, collection_name=collection_name, metadatas=metadatas, ids=ids, embedding_sizes=embedding_sizes, batch_size=batch_size, parallel=parallel)
    
    def search_vectors(self, project_id: str, query_vector: list, filters: Optional[Dict[str, Any]], top_k: int = 5) -> list:
        collection_name = self.create_collection_name(project_id)
        if not self.vector_client.is_collection_exists(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return []
        return self.vector_client.search(collection_name=collection_name, query_vector=query_vector, top_k=top_k, filters=filters)
    
    def get_collection_info(self, project_id: str) -> dict:
        collection_name = self.create_collection_name(project_id)
        if not self.vector_client.is_collection_exists(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return {}
        return self.vector_client.get_collection_info(collection_name=collection_name)
    
    def get_all_collections(self) -> list:
        return self.vector_client.get_all_collections()
    
    def index_into_vector_db(self, project: ProjectSchema,
                             chunks: List[ChunkSchema],
                             do_reset) -> bool:
        collection_name = self.create_collection_name(project.project_id)
        if do_reset:
            self.reset_collection(project_id=project.project_id)
        if not self.vector_client.is_collection_exists(collection_name):
            self.create_collection(project_id=project.project_id)
        texts = [chunk.page_content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        ids = [str(chunk.id) for chunk in chunks]
        vectors = [
            self.embedding_client.embed_text(text=text, doc_type=chunk.)
            for text in texts
        ]
    # Generation Operations
    def generate_text(self, prompt: str, chat_history: Optional[list] = None, temperature: float = 0.1, max_tokens: int = 1000) -> Optional[str]:
        return self.generation_client.generate_text(prompt=prompt, chat_history=chat_history, temperature=temperature, max_tokens=max_tokens)
    
    def count_tokens(self, text: str) -> int:
        return self.generation_client.count_tokens(text=text)
    
    # Embedding Operations
    def embed_text(self, text: str, doc_type: Optional[str] = None) -> Optional[list]:
        return self.embedding_client.embed_text(text=text, doc_type=doc_type)
    
    def process_text(self, text: str) -> str:
        return self.embedding_client.process_text(text=text)
    
    
    