from abc import ABC, abstractmethod

class EmbeddingInterface(ABC):
    
    @abstractmethod
    def set_embedding_model(self,model_id, embeding_size: int):
        pass
    
    @abstractmethod
    def embed_text(self, text: str, doc_type = None) -> list | None:
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        pass 