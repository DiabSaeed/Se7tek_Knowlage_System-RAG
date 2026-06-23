from abc import ABC, abstractmethod

from typing import Optional

class GenerationInterface(ABC):
    
    @abstractmethod
    def set_generation_model(self,model_id):
        pass
    
    @abstractmethod
    def generate_response(self, messages: list, temperature: float|None = None, max_tokens: int | None = None) -> str | None:
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        pass