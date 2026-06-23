from typing import List

from openai import OpenAI
from ...GenerationInterface import GenerationInterface
from ...EmbeddingInterface import EmbeddingInterface
import logging
from ...Enums.LlmEnums import OpenAiEnums, LlmEnums
import tiktoken

class OpenaiProvider(GenerationInterface, EmbeddingInterface):
    
    def __init__(self, 
                 open_ai_key: str,
                 base_url: str,
                 input_max_characters: int = 1000,
                 default_generation_max_tokens: int = 1000,
                 default_generation_temperature: float = 0.1
                 ): 
        
        self.open_ai_key = open_ai_key
        self.base_url = base_url
        self.input_max_characters = input_max_characters
        self.default_generation_max_tokens = default_generation_max_tokens
        self.default_generation_temperature = default_generation_temperature
        
        self.generation_model_id = None
        self.embedings_model_id = None
        self.embedings_size = None
        
        self.client = OpenAI(api_key=self.open_ai_key, base_url=self.base_url)
        self.logger = logging.getLogger(__name__)
        
    def set_generation_model(self, model_id):
        self.generation_model_id = model_id
        
    def set_embedding_model(self, model_id, embeding_size):
        self.embedings_model_id = model_id
        self.embedings_size = embeding_size 
        
    def generate_response(self, messages: list, temperature: float|None = None, max_tokens: int|None = None) -> str | None:
       
        if not self.client:
            self.logger.error("OpenAI Client is not initialized") 
            return None
            
        if not self.generation_model_id:
            self.logger.error("Generation model for OpenAI not set")
            return None
        
        # إعدادات الموديل
        max_output_tokens = max_tokens if max_tokens else self.default_generation_max_tokens
        temp = temperature if temperature is not None else self.default_generation_temperature
        
        try:
            response = self.client.chat.completions.create(
                model=self.generation_model_id,
                temperature=temp,
                max_tokens=max_output_tokens,
                messages=messages
            )
            
            if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
                self.logger.error("OpenAI did not respond properly")
                return None
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Error during text generation: {e}")
            return None

    def embed_text(self, text: str, doc_type = None):
        if not self.client:
            self.logger.error("OpenAI Client is not initialized") 
            return None
        if not self.embedings_model_id:
            self.logger.error("Embedding model for OpenAI not set")
            return None
            
        try:
            response = self.client.embeddings.create(
                model=self.embedings_model_id,
                input=text
            )

            if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
                self.logger.error("Error while embedding text")
                return None
            
            return response.data[0].embedding
            
        except Exception as e:
            self.logger.error(f"Error during text embedding: {e}")
            return None
        
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "content": self.process_text(prompt) 
        }
    
    def embed_texts(self, texts: List[str], doc_type=None) -> List[list]:
        raise NotImplementedError("Batch embedding is not implemented in OpenaiProvider. Use embed_text for individual text embedding.")
    
    def count_tokens(self, text: str):
        if not text:
            return 0
        try:
            encoding = tiktoken.encoding_for_model(str(self.generation_model_id))
        except KeyError:
            self.logger.warning(f"Model {self.generation_model_id} not found. Using default encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        return len(tokens)
    
    def process_text(self, text: str):
        return text[:self.input_max_characters]