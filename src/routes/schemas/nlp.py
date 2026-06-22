from pydantic import BaseModel, Field
from typing import List, Optional

class PushRequest(BaseModel):
    do_reset: Optional[int] = Field(description="Whether to reset existing data (1 for true, 0 for false)", default=0)
    page_size: int = Field(description="Number of chunks to process per page", default=10)

class SearchRequest(BaseModel):
    query_text: str = Field(description="The text to search for in the vector database")
    top_k: int = Field(description="Number of top results to return", default=5)
    doc_type: Optional[str] = Field(description="Type of document for embedding", default="text")
    filters: Optional[dict] = Field(description="Filters to apply during the search", default=None)


class GenerateRequest(BaseModel):
    query: str = Field(description="The prompt text for text generation")
    temperature: Optional[float] = Field(description="Sampling temperature for generation", default=0.1)
    max_tokens: Optional[int] = Field(description="Maximum number of tokens to generate", default=1000)