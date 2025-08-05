import enum


class DocumentStatusEnum(str, enum.Enum):
    uploaded = "uploaded"
    extracting = "extracting"
    extracted = "extracted"
    embedding = "embedding"
    embedded = "embedded"
    processed = "processed"
    extraction_failed = "extraction_failed"
    embedding_failed = "embedding_failed"


class DocumentTypeEnum(str, enum.Enum):
    pdf = "pdf"
    docx = "docx"
    txt = "txt"


class ChunkTypeEnum(str, enum.Enum):
    text = "text"
    size = "size"
    image = "image"
    table = "table"


class QueryStatusEnum(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class SimilarityTypeEnum(str, enum.Enum):
    cosine = "cosine"
    euclidean = "euclidean"
