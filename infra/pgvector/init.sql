/*
+-------------------+       +---------------------+       +---------------------+
|     document      |       |   document_chunk    |       |     query      |
+-------------------+       +---------------------+       +---------------------+
| PK | id           |<----->| PK | id             |       | PK | id           |
|    | tenant_id    |       |    | tenant_id      |<---+  |    | tenant_id    |
|    | name         |       |    | chunk_type     |    |  |    | query_text   |
|    | type         |       |    | chunk_text     |    |  |    | result       |
|    | created_at   |       |    | page_number    |    |  |    | status       |
|    | updated_at   |       |    | embedding      |    |  |    | created_at   |
+-------------------+       | FK | fk_document_id |    |  |    | updated_at   |
                            |    | created_at     |    |  +---------------------+
                            |    | updated_at     |    |            ^
                            +---------------------+    |            |
                                                       |            |
                                                       |            |
+------------------------------------------+          |            |
|       query_document_chunk          |          |            |
+------------------------------------------+          |            |
| PK | id                                 |           |            |
| FK | fk_document_chunk_id               |-----------+            |
| FK | fk_query_id                   |-----------------------+
|    | similarity_type                    |
|    | similarity_score                   |
|    | created_at                         |
|    | updated_at                         |
+------------------------------------------+


*/

-- Activate PGVector extension
CREATE EXTENSION IF NOT EXISTS vector;



-- CREATE UPDATED_AT FUNCTION
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;




---------------------------------------------DOCUMENT TABLE ------------------------------------------------------------------

CREATE TYPE document_status AS ENUM ('uploaded', 'processing', 'processed', 'erro_to_process');
CREATE TYPE document_type AS ENUM ('pdf', 'pdf_as_image', 'docx','pptx', 'csv');

-- Document main table
CREATE TABLE document (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL,
    name TEXT NOT NULL,
    status document_status NOT NULL DEFAULT 'uploaded',
    type document_type NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_document_id ON document(id);
CREATE INDEX idx_document_tenant_id ON document(tenant_id);


CREATE TRIGGER trigger_set_updated_at_document
BEFORE UPDATE ON document
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


------------------------------------------------------------------------------------------------------------------------------




---------------------------------------------DOCUMENT CHUNK TABLE ------------------------------------------------------------

CREATE TYPE chunk_type as ENUM ('paragraph', 'size', 'image', 'table');

CREATE TABLE document_chunk(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL,
    type chunk_type NOT NULL,
    chunk TEXT NOT NULL CHECK (chunk <> ''),  -- Equivalente ao min_length=1
    page_number INTEGER NOT NULL CHECK (page_number >= 0),
    embedding VECTOR(1536),  -- Ajuste a dimensão conforme seu modelo
    fk_document_id UUID NOT NULL REFERENCES document(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);



-- VECTOR INDEX FOR VECTOR SEARCH
CREATE INDEX idx_document_chunk_hnsw ON document_chunk
USING hnsw (embedding vector_cosine_ops)
WITH (
    m = 16,               -- Número máximo de conexões por nó (16-48)
    ef_construction = 64   -- Precisão durante construção (40-200)
);



CREATE INDEX idx_document_chunk_id ON document_chunk(id);
CREATE INDEX idx_document_chunk_tenant_id ON document_chunk(tenant_id);
CREATE INDEX idx_document_chunk_fk_doc_id ON document_chunk(fk_document_id);



CREATE TRIGGER trigger_set_updated_at_document_chunk
BEFORE UPDATE ON document_chunk
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


---------------------------------------------------------------------------------------------------------------------------






---------------------------------------------USER QUERY TABLE --------------------------------------------------------------

CREATE TYPE query_status AS ENUM ('pending', 'completed', 'failed');


CREATE TABLE IF NOT EXISTS query (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL,
    query_text TEXT,
    result TEXT,
    status query_status,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


CREATE INDEX idx_query_id ON query(id);
CREATE INDEX idx_query_tenant_id ON query(tenant_id);



CREATE TRIGGER trigger_set_updated_at_query
BEFORE UPDATE ON query
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();



------------------------------------------------------------------------------------------------------------------------------






---------------------------------------------USER QUERY DOCUMENT CHUNK TABLE -------------------------------------------------

CREATE TYPE similarity_type AS ENUM ('cosine', 'euclidean');
CREATE TYPE query_type as ENUM ('text', 'image', 'table');

CREATE TABLE IF NOT EXISTS query_document_chunk (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_document_chunk_id UUID NOT NULL REFERENCES document_chunk(id) ON DELETE CASCADE,
    fk_query_id UUID NOT NULL REFERENCES query(id) ON DELETE CASCADE,
    similarity_type similarity_type NOT NULL DEFAULT 'cosine',
    similarity_score FLOAT NOT NULL,
    type query_type NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


CREATE INDEX idx_query_document_chunk_fk_document_chunk_id_and_fk_query_id ON query_document_chunk(fk_document_chunk_id, fk_query_id);



CREATE TRIGGER trigger_set_updated_at_query_document_chunk
BEFORE UPDATE ON query_document_chunk
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();
