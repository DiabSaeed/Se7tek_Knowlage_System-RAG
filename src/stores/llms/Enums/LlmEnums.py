from enum import Enum

class LlmEnums(Enum):
    OPENAI="OpenAI"
    COHERE = "Cohere"
    OLLAMA = "OLLAMA"
    BGEM3 = "BGEM3"
    
    # Roles 
class OpenAiEnums(Enum):
    SYSTEM = "system"
    ASSISTENT = "assistant"
    USER = "user"
    
class OpenRouterEnums(Enum):
    SYSTEM = "system"
    ASSISTENT = "assistant"
    USER = "user"