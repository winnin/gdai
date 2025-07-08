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

CREATE TYPE document_type AS ENUM ('pdf', 'pdf_as_image', 'docx','pptx', 'csv');

-- Document main table
CREATE TABLE document (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL,
    name TEXT NOT NULL,
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
    chunk_type chunk_type NOT NULL,
    chunk_text TEXT NOT NULL CHECK (chunk_text <> ''),  -- Equivalente ao min_length=1
    page_number INTEGER NOT NULL CHECK (page_number >= 0),
    embedding VECTOR(1536),  -- Ajuste a dimensão conforme seu modelo
    fk_document_id UUID NOT NULL REFERENCES document(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)



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


CREATE TABLE IF NOT EXISTS user_query (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL,
    query_text TEXT,
    result TEXT,
    status query_status,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


CREATE INDEX idx_user_query_id ON user_query(id);
CREATE INDEX idx_user_query_tenant_id ON user_query(tenant_id);



CREATE TRIGGER trigger_set_updated_at_user_query
BEFORE UPDATE ON user_query
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();



------------------------------------------------------------------------------------------------------------------------------






---------------------------------------------USER QUERY DOCUMENT CHUNK TABLE -------------------------------------------------

CREATE TYPE similarity_type AS ENUM ('cosine', 'euclidean');


CREATE TABLE IF NOT EXISTS user_query_document_chunk (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_document_chunk_id UUID NOT NULL REFERENCES document_chunk(id) ON DELETE CASCADE,
    fk_user_query_id UUID NOT NULL REFERENCES user_query(id) ON DELETE CASCADE,
    similarity_type similarity_type NOT NULL DEFAULT 'cosine',
    similarity_score FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


CREATE INDEX idx_user_query_document_chunk_fk_document_chunk_id_and_fk_user_query_id ON user_query_document_chunk(fk_document_chunk_id, fk_user_query_id);



CREATE TRIGGER trigger_set_updated_at_user_query_document_chunk
BEFORE UPDATE ON user_query_document_chunk
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();
