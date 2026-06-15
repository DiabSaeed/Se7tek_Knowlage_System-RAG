from pydantic import BaseModel
from typing import Optional
class ProcessRequest(BaseModel):
    file_id: Optional[str] = None
    chunk_size : int = 1000
    chunk_overlab: int = 200
    do_reset: Optional[int] = 0 