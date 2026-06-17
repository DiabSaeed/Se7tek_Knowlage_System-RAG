from openai import OpenAI
from ..LlmInterface import LlmInterface
import logging
from ..Enums.LlmEnums import OpenAiEnums, LlmEnums
import tiktoken

class OpenaiProvider(LlmInterface):
    
    def __init__(self, 
                 open_ai_key: str,
                 input_max_characters: int = 1000,
                 default_generation_max_tokens: int = 1000,
                 default_generation_tempreture: float = .1):
        
        self.open_ai_key = open_ai_key
        self.input_max_characters = input_max_characters
        self.default_generation_max_tokens = default_generation_max_tokens
        self.default_generation_tempreture = default_generation_tempreture
        
        self.generation_model_id = None
        self.embedings_model_id = None
        self.embedings_size = None
        
        self.client = OpenAI(
            api_key= self.open_ai_key
            )
        self.logger = logging.getLogger(__name__)
        
    def set_generation_model(self, model_id):
        self.generation_model_id = model_id
        
    def set_embedding_model(self, model_id, embeding_size):
        self.embedings_model_id = model_id
        self.embedings_size = self.embedings_size
        
    def generate_text(self, prompt: str, chat_history: list = [], tempreture: float = 0.1, max_tokens: int = 1000) -> str | None:
        if not self.client:
            self.logger.error("There is no chat history")
            return None
        if not self.generation_model_id:
            self.logger.error("Generation model for OpenAI not set")
            return None
        
        max_output_tokens = max_tokens if max_tokens else self.default_generation_max_tokens
        tempreture = tempreture if tempreture else self.default_generation_tempreture
        chat_history.append(self.construct_prompt(
            prompt= prompt,
            role= OpenAiEnums.USER.value
        ))
        
        response = self.client.chat.completions.create(
            model= self.generation_model_id,
            temperature= tempreture,
            max_tokens= max_output_tokens,
            messages= chat_history
        )
        if not response or not response.choices or len(response.choices) == 0 or response.choices[0].message:
            self.logger.error("OpenAI is not responed")
            return None
        
        return response.choices[0].message.content
    def embed_text(self, text: str, doc_type = None):
        if not self.client:
            self.logger.error("There is no chat history")
            return None
        if not self.embedings_model_id:
            self.logger.error("Embeding model for OpenAI not set")
            return None
        response = self.client.embeddings.create(
            model= self.embedings_model_id,
            input= text
        )

        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
            self.logger.error("Error while embeding text")
            return None
        
        return response.data[0].embedding
        
    def construct_prompt(self,prompt: str, role:str):
        return {
            "role": role,
            "prompt": self.process_text(prompt)
        }
    
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
        return text [:self.input_max_characters].strip()