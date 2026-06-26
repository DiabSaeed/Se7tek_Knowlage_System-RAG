from pydantic import BaseModel
from typing import Optional
class ProcessRequest(BaseModel):
    file_id: Optional[str] = None
    chunk_size : Optional[int] 
    chunk_overlab: Optional[int]
    do_reset: Optional[int] = 0 