-- Activate PGVector extension
CREATE EXTENSION IF NOT EXISTS vector;




------------------------------------------ENUMS AND TYPES-----------------------------------------------------
-- Document Status Enum
DROP TYPE IF EXISTS documentstatusenum CASCADE;
CREATE TYPE documentstatusenum AS ENUM (
    'uploaded',
    'extracting',
    'extracted',
    'embedding',
    'embedded',
    'processed',
    'extraction_failed',
    'embedding_failed'
);

-- Document Type Enum
DROP TYPE IF EXISTS documenttypeenum CASCADE;
CREATE TYPE documenttypeenum AS ENUM (
    'pdf',
    'docx',
    'txt'
);

-- Chunk Type Enum
DROP TYPE IF EXISTS chunktypeenum CASCADE;
CREATE TYPE chunktypeenum AS ENUM (
    'text',
    'size',
    'image',
    'table'
);

-- Query Status Enum
DROP TYPE IF EXISTS querystatusenum CASCADE;
CREATE TYPE querystatusenum AS ENUM (
    'pending',
    'completed',
    'failed'
);

-- Similarity Type Enum
DROP TYPE IF EXISTS similaritytypeenum CASCADE;
CREATE TYPE similaritytypeenum AS ENUM (
    'cosine',
    'euclidean'
);





---------------------------------------------DOCUMENT TABLE ------------------------------------------------------------------

-- Document main table
CREATE TABLE document (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL,
    name VARCHAR NOT NULL,
    status documentstatusenum NOT NULL,
    chunk_strategy VARCHAR(64),
    type documenttypeenum NOT NULL,
    retry_extraction INTEGER DEFAULT 0 CHECK (retry_extraction >= 0),
    retry_embedding INTEGER DEFAULT 0 CHECK (retry_embedding >= 0),
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE INDEX idx_document_id ON document(id);
CREATE INDEX idx_document_tenant_id ON document(tenant_id);

------------------------------------------------------------------------------------------------------------------------------




---------------------------------------------DOCUMENT CHUNK TABLE ------------------------------------------------------------


CREATE TABLE chunk(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL,
    type chunktypeenum NOT NULL,
    chunk TEXT NOT NULL CHECK (chunk <> ''),  -- Equivalente ao min_length=1
    page_number INTEGER NOT NULL CHECK (page_number >= 0),
    embedding VECTOR(1536),
    document_id UUID NOT NULL REFERENCES document(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITHOUT TIME ZONE,
    updated_at TIMESTAMP WITHOUT TIME ZONE
);



-- VECTOR INDEX FOR VECTOR SEARCH
CREATE INDEX idx_chunk_hnsw ON chunk
USING hnsw (embedding vector_cosine_ops)
WITH (
    m = 16,               -- Max number of connections per node (16-48)
    ef_construction = 64   -- Precision during construction (40-200)
);



CREATE INDEX idx_chunk_id ON chunk(id);
CREATE INDEX idx_chunk_tenant_id ON chunk(tenant_id);
CREATE INDEX idx_chunk_doc_id ON chunk(document_id);


---------------------------------------------------------------------------------------------------------------------------





---------------------------------------------USER QUERY TABLE --------------------------------------------------------------


CREATE TABLE IF NOT EXISTS query (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL,
    query TEXT,
    result TEXT,
    status querystatusenum NOT NULL,
    similarity similaritytypeenum NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE,
    updated_at TIMESTAMP WITHOUT TIME ZONE
);


CREATE INDEX idx_query_id ON query(id);
CREATE INDEX idx_query_tenant_id ON query(tenant_id);


------------------------------------------------------------------------------------------------------------------------------






---------------------------------------------USER QUERY DOCUMENT CHUNK TABLE -------------------------------------------------

CREATE TABLE query_chunk_link (
        query_id UUID NOT NULL,
        chunk_id UUID NOT NULL,
        similarity_score FLOAT NOT NULL,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        PRIMARY KEY (query_id, chunk_id),
        FOREIGN KEY(query_id) REFERENCES query (id),
        FOREIGN KEY(chunk_id) REFERENCES chunk (id)
);

CREATE INDEX idx_query_chunk_link_chunk_id_query_id ON query_chunk_link(chunk_id, query_id);
