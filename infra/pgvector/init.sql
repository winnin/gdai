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
+-------------------+       | FK | document_id |    |  |    | updated_at   |
                            |    | created_at     |    |  +---------------------+
                            |    | updated_at     |    |            ^
                            +---------------------+    |            |
                                                       |            |
                                                       |            |
+------------------------------------------+          |            |
|       query_document_chunk          |          |            |
+------------------------------------------+          |            |
| PK | id                                 |           |            |
| FK | document_chunk_id               |-----------+            |
| FK | query_id                   |-----------------------+
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

-- Document main table
CREATE TABLE document (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL,
    name TEXT NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'uploaded',
    type VARCHAR(16) NOT NULL,
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


CREATE TABLE document_chunk(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL,
    type VARCHAR(16) NOT NULL,
    chunk TEXT NOT NULL CHECK (chunk <> ''),  -- Equivalente ao min_length=1
    page_number INTEGER NOT NULL CHECK (page_number >= 0),
    embedding VECTOR(1536),  -- Ajuste a dimensão conforme seu modelo
    document_id UUID NOT NULL REFERENCES document(id) ON DELETE CASCADE,
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
CREATE INDEX idx_document_chunk_doc_id ON document_chunk(document_id);



CREATE TRIGGER trigger_set_updated_at_document_chunk
BEFORE UPDATE ON document_chunk
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


---------------------------------------------------------------------------------------------------------------------------






---------------------------------------------USER QUERY TABLE --------------------------------------------------------------


CREATE TABLE IF NOT EXISTS query (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL,
    query_text TEXT,
    result TEXT,
    status VARCHAR(16) NOT NULL DEFAULT 'pending',
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

CREATE TABLE IF NOT EXISTS query_document_chunk (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_chunk_id UUID NOT NULL REFERENCES document_chunk(id) ON DELETE CASCADE,
    query_id UUID NOT NULL REFERENCES query(id) ON DELETE CASCADE,
    similarity_type VARCHAR(16) NOT NULL DEFAULT 'cosine',
    similarity_score FLOAT NOT NULL,
    type VARCHAR(16) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


CREATE INDEX idx_query_document_chunk_document_chunk_id_and_query_id ON query_document_chunk(document_chunk_id, query_id);



CREATE TRIGGER trigger_set_updated_at_query_document_chunk
BEFORE UPDATE ON query_document_chunk
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();
