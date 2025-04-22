from enum import Enum

class VectorDBEnum(Enum):
    QDRANT='QDRANT'
    PGVECTOR='PGVECTOR'

    

class DistanceMethodEnums(Enum):
    COSINE = "cosine"
    DOT = "dot"

class PgvectorTableEnum(Enum):
    ID="id"
    TEXT="text"
    VECTOR="vector"
    CHUNK_ID="chunk_id"
    METADATA="metadata"
    _PREFIX="pgvector"


class PgvectorDistanceMethodEnum(Enum):
    COSINE = "vector_cosine_ops"
    DOT = "vector_l2_ops" 

class PgvectorIndexTypeEnum(Enum):
   HNSW = "hnsw"
   IVFFLAT = "ivfflat"