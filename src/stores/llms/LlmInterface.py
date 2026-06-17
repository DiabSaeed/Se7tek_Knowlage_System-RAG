from abc import ABC, abstractmethod

class LlmInterface(ABC):
    
    @abstractmethod
    def set_generation_model(self,model_id):
        pass
    
    @abstractmethod
    def set_embedding_model(self,model_id, embeding_size: int):
        pass
    
    @abstractmethod
    def generate_text(self, prompt: str, chat_history: list = [] , tempreture:float = .7, max_tokens: int = 1000 ) -> str | None:
        pass
    
    @abstractmethod
    def embed_text(self, text: str, doc_type = None) -> list | None:
        pass
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        pass 
    
    