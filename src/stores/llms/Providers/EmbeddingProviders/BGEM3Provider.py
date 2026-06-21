import logging
from FlagEmbedding import BGEM3FlagModel
from ...EmbeddingInterface import EmbeddingInterface
import re
import tiktoken
from typing import List, cast
import numpy as np

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
    
    
    def embed_texts(self, texts: List[str], doc_type = None) -> List[list]:
        if not self.embed_model:
            self.logger.error("BGE-M3 model is not loaded. Please call set_embedding_model() first.")
            return []
            
        cleaned_texts = [self.process_text(text) for text in texts if text and text.strip()]
        
        if not cleaned_texts:
            self.logger.warning("No valid or non-empty texts provided for embedding.")
            return []

        try:
            embeddings = self.embed_model.encode(
                cleaned_texts, 
                return_dense=True, 
                return_sparse=False, 
                return_colbert_vecs=False
            )
            dense_vecs_list = cast(List[np.ndarray], embeddings['dense_vecs'])
            
            dense_vectors = [vec.tolist() for vec in dense_vecs_list]
            
            if self.embedding_size and dense_vectors and len(dense_vectors[0]) != self.embedding_size:
                self.logger.warning(f"Expected embedding size {self.embedding_size}, but got {len(dense_vectors[0])}")
                
            return dense_vectors
            
        except Exception as e:
            self.logger.error(f"Error during batch text embedding with BGE-M3: {e}")
            return []
    
    def process_text(self, text: str):
        
        if not text:
            return ""
        text = text.lower().strip()
        text = re.sub(r'[\u064B-\u065F]', '', text)
        text = re.sub(r'[أإآ]', 'ا', text)
        text = re.sub(r'ة', 'ه', text)
        return text
    def count_tokens(self, text: str):
        if not text:
            return 0
        try:
            encoding = tiktoken.encoding_for_model(str(self.embedding_model_id))
        except KeyError:
            self.logger.warning(f"Model {self.embedding_model_id} not found. Using default encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        return len(tokens)
