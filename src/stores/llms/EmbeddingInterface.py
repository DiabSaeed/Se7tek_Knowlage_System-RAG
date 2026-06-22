from abc import ABC, abstractmethod
from typing import List

class EmbeddingInterface(ABC):
    
    @abstractmethod
    def set_embedding_model(self,model_id, embeding_size: int):
        pass
    
    @abstractmethod
    def embed_text(self, text: str, doc_type = None) -> list | None:
        pass
    
    @abstractmethod
    def embed_texts(self, texts: List[str], doc_type = None) -> List[list]:
        pass
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        pass 
    
    @abstractmethod
    def process_text(self, text: str) -> str:
        pass