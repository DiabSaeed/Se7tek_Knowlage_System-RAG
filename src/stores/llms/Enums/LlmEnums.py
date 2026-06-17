from enum import Enum

class LlmEnums(Enum):
    OPENAI="OpenAI"
    COHERE = "Cohere"
    OLLAMA = "OLLAMA"
    
    # Roles 
class OpenAiEnums(Enum):
    SYSTEM = "system"
    ASSISTENT = "assistant"
    USER = "user"