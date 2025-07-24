import enum


class DocumentStatusEnum(str, enum.Enum):
    uploaded = "uploaded"
    processing = "processing"
    processed = "processed"
    failed = "failed"


class DocumentTypeEnum(str, enum.Enum):
    pdf = "pdf"
    docx = "docx"
    txt = "txt"


class ChunkTypeEnum(str, enum.Enum):
    paragraph = "paragraph"
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
