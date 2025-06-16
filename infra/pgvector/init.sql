-- Ativa a extensão PGvector (caso não esteja ativada)
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabela principal de documentos
CREATE TABLE document (
    id VARCHAR(64) PRIMARY KEY,
    name TEXT NOT NULL,
    tenant_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- Tabela de chunk dos documentos com vetores
CREATE TABLE document_chunk (
    id VARCHAR(512) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    chunk_text TEXT NOT NULL CHECK (chunk_text <> ''),  -- Equivalente ao min_length=1
    page_number INTEGER NOT NULL CHECK (page_number >= 0),
    begin_offset INTEGER NOT NULL CHECK (begin_offset >= 0),
    end_offset INTEGER NOT NULL CHECK (end_offset >= 0),
    embedding VECTOR(1536),  -- Ajuste a dimensão conforme seu modelo
    fk_doc_id VARCHAR(64) NOT NULL REFERENCES document(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para buscas vetoriais (ajuste lists conforme seu dataset)
CREATE INDEX idx_document_chunk_hnsw ON document_chunk
USING hnsw (embedding vector_cosine_ops)
WITH (
    m = 16,               -- Número máximo de conexões por nó (16-48)
    ef_construction = 64   -- Precisão durante construção (40-200)
);

-- Índice para melhor performance nas relações
CREATE INDEX idx_document_chunk_fk_doc_id ON document_chunk(fk_doc_id);



-------------------------------------------------------
DO $$ BEGIN
    CREATE TYPE message_status AS ENUM ('pending', 'completed', 'failed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;



CREATE TABLE IF NOT EXISTS message (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL,
    query_id VARCHAR(64),
    query_text text,
    result TEXT,
    status message_status,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


CREATE INDEX idx_message_tenant_id_and_query_id ON message(tenant_id, query_id);
CREATE INDEX idx_message_status ON message(status);


-------------------------------------------------------

CREATE TABLE IF NOT EXISTS token (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_message_id UUID REFERENCES message(id),
    token_number INTEGER,
    token_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()

);

CREATE INDEX idx_token_fk_message_id ON token(fk_message_id);

-------------------------------------------------------

CREATE TABLE chunk_message (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_document_chunk_id VARCHAR(512) NOT NULL REFERENCES document_chunk(id) ON DELETE CASCADE,
    fk_message_id UUID NOT NULL REFERENCES message(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_chunk_message_fk_document_chunk_id_and_fk_message_id ON chunk_message(fk_document_chunk_id, fk_message_id);

-------------------------------------------------------

-- Authentication & Authorization tables
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    tenant_id VARCHAR(64) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(32) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS user_roles (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- Seed roles
do $$
begin
    if not exists (select 1 from roles where name = 'god') then
        insert into roles (name) values ('god');
    end if;
    if not exists (select 1 from roles where name = 'manager') then
        insert into roles (name) values ('manager');
    end if;
    if not exists (select 1 from roles where name = 'user') then
        insert into roles (name) values ('user');
    end if;
end$$;
