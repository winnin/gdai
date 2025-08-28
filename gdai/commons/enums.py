import enum


class DocumentStatusEnum(str, enum.Enum):
    processed = "processed"
    extraction_failed = "extraction_failed"
    embedding_failed = "embedding_failed"


class DocumentTypeEnum(str, enum.Enum):
    pdf = "pdf"


class ChunkTypeEnum(str, enum.Enum):
    text = "text"
    image = "image"
    table = "table"


class QueryStatusEnum(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
