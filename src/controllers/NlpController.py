from .BaseController import BaseController
from stores.llms.EmbeddingInterface import EmbeddingInterface
from stores.llms.GenerationInterface import GenerationInterface
from stores.VectorDB.VectorDBInterface import VectorDBInterface
from models.db_schema import ProjectSchema, ChunkSchema
from models.enums.DocumentTypeEnums import DocumentTypeEnums
from stores.llms.templates import PromptParser
from typing import List, Optional, Dict, Any, cast
import logging
import uuid

class NlpController(BaseController):
    def __init__(self, vector_client: VectorDBInterface, embedding_client: EmbeddingInterface, generation_client: GenerationInterface, prompt_parser: PromptParser):
        super().__init__()
        self.vector_client = vector_client
        self.embedding_client = embedding_client
        self.generation_client = generation_client
        self.prompt_parser = prompt_parser
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
            info = self.vector_client.get_collection_info(collection_name)
            print(info)
            return True
        self.logger.warning(f"Collection {collection_name} already exists.")
        return False
    
    def insert_vector(self, project_id: str, vector: list, text: str, metadata: Dict[str, Any], id: str, embedding_size: int) -> bool:
        collection_name = self.create_collection_name(project_id)
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
    
    def search_vectors(self, project_id: str, query_vector: list, query_text, filters: Optional[Dict[str, Any]], top_k: int = 5) -> list:
        collection_name = self.create_collection_name(project_id)
        if not self.vector_client.is_collection_exists(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return []
        return self.vector_client.search(collection_name=collection_name, query_vector=query_vector, query_text=query_text, top_k=top_k, filters=filters)
    
    def get_collection_info(self, project_id: str) -> dict:
        collection_name = self.create_collection_name(project_id)
        if not self.vector_client.is_collection_exists(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return {}
        return self.vector_client.get_collection_info(collection_name=collection_name)
    
    def get_all_collections(self) -> list:
        return self.vector_client.get_all_collections()
    
    def index_into_vector_db(self, project: ProjectSchema, chunks: List[ChunkSchema], doc_type: Optional[str] = None) -> bool:
        collection_name = self.create_collection_name(project.project_id)
        if not self.vector_client.is_collection_exists(collection_name):
            self.create_collection(project_id=project.project_id)
            
        texts = [chunk.page_content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]  
        ids = [self._objet_id_to_uuid(str(chunk.id)) for chunk in chunks]
        
      
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
    def _objet_id_to_uuid(self, object_id:str) -> str:
        padded_hex = object_id.zfill(32)
        return str(uuid.UUID(padded_hex))
    # ==========================================
    # Generation Operations
    # ==========================================
    def generate_text(self, prompt: List[str], chat_history: Optional[list] = None, temperature: float = 0.1, max_tokens: int = 1000) -> Optional[str]:
        return self.generation_client.generate_response(messages=prompt, temperature=temperature, max_tokens=max_tokens)
    
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
    
    # ==========================================
    # Prompt Operations
    # ==========================================
    def build_rag_prompt(self, query: str,project_id: str, tone: str = "professional") -> list:
        if not self.vector_client.is_collection_exists(self.create_collection_name(project_id=project_id)):
            self.logger.error(f"Collection for project {project_id} does not exist.")
            return []
        query_vector = self.embed_text(text=query)
        if not query_vector:
            self.logger.error("Failed to generate embedding for the query.")
            return []
        context_chunks = self.vector_client.search(collection_name=self.create_collection_name(project_id=project_id),
                                                   query_vector=query_vector,
                                                   query_text= query,
                                                   top_k=10)
        clean_texts = [hit["text"] for hit in context_chunks]
        messages = self.prompt_parser.build_rag_prompt(query=query, context_chunks=clean_texts)
        print(f"--- Prepared Messages for LLM: {messages} ---")
        return messages