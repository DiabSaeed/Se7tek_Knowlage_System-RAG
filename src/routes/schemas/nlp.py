from pydantic import BaseModel, Field
from typing import List, Optional

class PushRequest(BaseModel):
    do_reset: Optional[int] = Field(description="Whether to reset existing data (1 for true, 0 for false)", default=0)
    