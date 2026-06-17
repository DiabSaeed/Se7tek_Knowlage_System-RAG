import logging
from FlagEmbedding import BGEM3FlagModel
from ...EmbeddingInterface import EmbeddingInterface
import re

class BGEM3Provider(EmbeddingInterface):
    def __init__(self):
        self.embed_model = None
        self.embedding_size = None
        self.embedding_model_id = None
        self.logger = logging.getLogger(__name__)
    
    def set_embedding_model(self, model_id = "BAAI/bge-m3", embeding_size: int = 1024):
        self.embedding_model_id = model_id
        self.embedding_size = embeding_size
        self.logger.info(f"Loading BGE-M3 model: {self.embedding_model_id}. This might take a moment...")
    
        try:
            self.embed_model = BGEM3FlagModel(self.embedding_model_id, use_fp16=True)
            self.logger.info("BGE-M3 model loaded successfully.")
        except Exception as e:
            self.logger.error(f"Failed to load BGE-M3 model: {e}")
    def embed_text(self, text: str, doc_type = None) -> list | None:
        """
        تحويل النص إلى أرقام (Dense Vector).
        """
        if not self.embed_model:
            self.logger.error("BGE-M3 model is not loaded. Please call set_embedding_model() first.")
            return None
            
        if not text or not text.strip():
            self.logger.warning("Empty text provided for embedding.")
            return None

        try:
            
            embeddings = self.embed_model.encode(
                [self.process_text(text)], 
                return_dense=True, 
                return_sparse=False, 
                return_colbert_vecs=False
            )
            
            dense_vector = embeddings['dense_vecs'][0].tolist() #type: ignore 
            
            if self.embedding_size and len(dense_vector) != self.embedding_size:
                self.logger.warning(f"Expected embedding size {self.embedding_size}, but got {len(dense_vector)}")
                
            return dense_vector
            
        except Exception as e:
            self.logger.error(f"Error during text embedding with BGE-M3: {e}")
            return None
        
    def process_text(self, text: str):
        
        if not text:
            return ""
        text = text.lower().strip()
        text = re.sub(r'[\u064B-\u065F]', '', text)
        text = re.sub(r'[أإآ]', 'ا', text)
        text = re.sub(r'ة', 'ه', text)
        return text