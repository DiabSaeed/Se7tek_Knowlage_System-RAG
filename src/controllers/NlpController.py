from typing import List, Optional, Dict, Any, cast
import logging

from .BaseController import BaseController
from stores.VectorDB.Provider.QdranDB import QdrantDB
from stores.llms.Providers.GeneralProviders.OpenAIProvider import OpenaiProvider
from stores.llms.Providers.EmbeddingProviders.BGEM3Provider import BGEM3Provider
from models.db_schema import ProjectSchema, ChunkSchema
from models.enums.DocumentTypeEnums import DocumentTypeEnums

class NlpController(BaseController):
    def __init__(self, vector_client: QdrantDB, embedding_client: BGEM3Provider, generation_client: OpenaiProvider):
        super().__init__()
        self.vector_client = vector_client
        self.embedding_client = embedding_client
        self.generation_client = generation_client
        self.logger = logging.getLogger(__name__)
    
    def create_collection_name(self, project_id: str) -> str:
        return f"collection_{project_id}"
    
    # ==========================================
    # VectorDB Operations
    # ==========================================
    def reset_collection(self, project_id: str) -> bool:
        collection_name = self.create_collection_name(project_id)
        if self.vector_client.is_collection_exists(collection_name):
            self.vector_client.delete_collection(collection_name=collection_name)
            return True
        self.logger.warning(f"Collection {collection_name} does not exist.")
        return False
        
    def create_collection(self, project_id: str, embedding_size: int = 1024) -> bool:
        collection_name = self.create_collection_name(project_id)
        if not self.vector_client.is_collection_exists(collection_name):
            self.vector_client.create_collection(collection_name=collection_name, embedding_size=embedding_size)
            return True
        self.logger.warning(f"Collection {collection_name} already exists.")
        return False
    
    def insert_vector(self, project_id: str, vector: list, text: str, metadata: Dict[str, Any], id: str, embedding_size: int) -> bool:
        collection_name = self.create_collection_name(project_id)
        # ملاحظة: يفضل مستقبلاً الاعتماد على Try/Except عوضاً عن الـ Check المتكرر لتوفير الـ Network Call
        if not self.vector_client.is_collection_exists(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return False
        return self.vector_client.insert_one_vector(
            vector=vector, text=text, collection_name=collection_name, metadata=metadata, id=id, embedding_size=embedding_size
        )
    
    def insert_vectors(self, project_id: str, vectors: List[list], texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str], embedding_sizes: List[int], batch_size: int = 64, parallel: int = 2) -> bool:
        collection_name = self.create_collection_name(project_id)
        if not self.vector_client.is_collection_exists(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return False
        return self.vector_client.insert_many(
            vectors=vectors, texts=texts, collection_name=collection_name, metadatas=metadatas, ids=ids, embedding_sizes=embedding_sizes, batch_size=batch_size, parallel=parallel
        )
    
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
    
    def index_into_vector_db(self, project: ProjectSchema, chunks: List[ChunkSchema], do_reset: bool, doc_type: Optional[str] = None) -> bool:
        collection_name = self.create_collection_name(project.project_id)
        
        if do_reset:
            self.reset_collection(project_id=project.project_id)
            
        if not self.vector_client.is_collection_exists(collection_name):
            self.create_collection(project_id=project.project_id)
            
        texts = [chunk.page_content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]  
        ids = [str(chunk.id) for chunk in chunks]
        
      
        if hasattr(self.embedding_client, 'embed_texts'):
            vectors = self.embedding_client.embed_texts(texts=texts, doc_type=doc_type or DocumentTypeEnums.PDF.value)
        else:
            vectors = [
                self.embedding_client.embed_text(text=text, doc_type=doc_type or DocumentTypeEnums.PDF.value)
                for text in texts
            ]
            
        vectors = cast(List[list], vectors)
        
        _ = self.vector_client.insert_many(
            vectors=vectors,
            texts=texts,
            collection_name=collection_name,
            metadatas=metadatas, 
            ids=ids,
            embedding_sizes=[len(vector) for vector in vectors],
            batch_size=64,
            parallel=2
        )
        return True

    # ==========================================
    # Generation Operations
    # ==========================================
    def generate_text(self, prompt: str, chat_history: Optional[list] = None, temperature: float = 0.1, max_tokens: int = 1000) -> Optional[str]:
        return self.generation_client.generate_text(prompt=prompt, chat_history=chat_history, temperature=temperature, max_tokens=max_tokens)
    
    def count_tokens(self, text: str) -> int:
        return self.generation_client.count_tokens(text=text)
    
    # ==========================================
    # Embedding Operations
    # ==========================================
    def embed_text(self, text: str, doc_type: Optional[str] = None) -> Optional[list]:
        return self.embedding_client.embed_text(text=text, doc_type=doc_type)
    
    def process_text(self, text: str) -> str:
        return self.embedding_client.process_text(text=text)
    
    def embed_texts(self, texts: List[str], doc_type: Optional[str] = None) -> List[list]:
        return self.embedding_client.embed_texts(texts=texts, doc_type=doc_type)