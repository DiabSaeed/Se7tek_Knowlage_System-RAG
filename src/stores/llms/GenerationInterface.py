from abc import ABC, abstractmethod

class GenerationInterface(ABC):
    
    @abstractmethod
    def set_generation_model(self,model_id):
        pass
    
    @abstractmethod
    def generate_text(self, prompt: str, chat_history: list , temperature:float = .1, max_tokens: int = 1000 ) -> str | None:
        pass