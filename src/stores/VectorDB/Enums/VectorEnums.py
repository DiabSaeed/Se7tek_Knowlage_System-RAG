from enum import Enum

class QdrantEnums(Enum):
    DBName = "Qdrant"
    FETCH_K = 20
class DistanceEnums(Enum):
    DOT = "dot"
    COSINE = "cosine"