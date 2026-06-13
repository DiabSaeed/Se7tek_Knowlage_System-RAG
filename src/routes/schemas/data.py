from pydantic import BaseModel
from typing import Optional
class ProcessRequest(BaseModel):
    file_id: str
    chunk_size : Optional[int] = 1000
    chunk_overlab: Optional[int] = 200
    do_reset: Optional[int] = 0 