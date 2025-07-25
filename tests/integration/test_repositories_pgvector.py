# class TestPGVectorDocumentRepository:
#     """Test suite for the PGVectorDocumentRepository."""

#     @pytest.mark.asyncio
#     async def test_insert_get_and_delete_document(self):
#         repo = PGVectorDocumentRepository()
#         tenant_id = "test-tenant-insert"
#         doc_id = uuid.uuid4()
#         document = Document(
#             id=doc_id, tenant_id=tenant_id, name="Documento de Teste", status="processed", type="pdf", texts=[]
#         )

#         await repo.insert(tenant_id, document)

#         result = await repo.get_by_id(tenant_id, doc_id)

#         assert result is not None
#         assert result.id == doc_id
#         assert result.tenant_id == tenant_id
#         assert result.name == "Documento de Teste"
#         # cleaning
#         await repo.delete(tenant_id, doc_id)


# class TestPGVectorDocumentChunkRepository:
#     """Test suite for the PGVectorDocumentChunkRepository."""

#     @pytest.mark.asyncio
#     async def test_insert_get_and_delete_document_chunk(self):
#         repo_doc = PGVectorDocumentRepository()
#         repo_chunk = PGVectorChunkRepository()

#         tenant_id = "test-tenant-chunk"
#         doc_id = str(uuid.uuid4())
#         chunk_id = str(uuid.uuid4())

#         # Insert document without chunks
#         document = Document(
#             id=doc_id,
#             tenant_id=tenant_id,
#             name="Documento para Chunk",
#             status=DocumentStatusEnum.uploaded,
#             type=DocumentTypeEnum.pdf,
#             chunks=[],
#         )
#         await repo_doc.insert(tenant_id, document)

#         # create  chunks
#         chunk = Chunk(
#             id=chunk_id,
#             tenant_id=tenant_id,
#             document_id=doc_id,
#             type=ChunkTypeEnum.paragraph,
#             chunk="Content of the test chunk.",
#             page_number=1,
#             embedding=[0.1] * 1536,
#         )
#         await repo_chunk.insert(tenant_id, chunk)

#         result = await repo_chunk.get_by_id(tenant_id, chunk_id)

#         assert result is not None
#         assert result.id == chunk_id
#         assert result.tenant_id == tenant_id
#         assert result.document_id == doc_id
#         assert result.chunk == "Conteúdo do chunk de teste."
#         # cleaning
#         await repo_chunk.delete(tenant_id, chunk_id)
#         await repo_doc.delete(tenant_id, doc_id)


# class TestPGVectorQueryRepository:
#     """Test suite for the PGVectorQueryRepository."""

#     @pytest.mark.asyncio
#     async def test_insert_get_and_delete_query(self):
#         repo_doc = PGVectorDocumentRepository()
#         repo_chunk = PGVectorDocumentChunkRepository()
#         repo_query = PGVectorQueryRepository()
#         tenant_id = "test-tenant-query"
#         doc_id = str(uuid.uuid4())
#         chunk_id = str(uuid.uuid4())
#         query_id = str(uuid.uuid4())

#         # Insert the document
#         document = Document(id=doc_id, tenant_id=tenant_id, name="Document for Query", status="processed", type="pdf",
# texts=[])
#         await repo_doc.insert(tenant_id, document)

#         # Insert the chunk related to the document
#         chunk = DocumentChunk(
#             id=chunk_id,
#             tenant_id=tenant_id,
#             document_id=doc_id,
#             type="paragraph",
#             chunk="Chunk for Query",
#             page_number=1,
#             embedding=[0.1] * 1536,
#             created_at=None,
#             updated_at=None,
#         )

#         await repo_chunk.insert(tenant_id, chunk)

#         # Insert the query
#         query = Query(
#             id=query_id,
#             tenant_id=tenant_id,
#             query="What is the document content?",
#             result="Found content.",
#             status="completed",
#             created_at=None,
#             updated_at=None,
#         )

#         await repo_query.insert(tenant_id, query)
#         result = await repo_query.get_by_id(tenant_id, query_id)
#         assert result is not None
#         # assert result.id == query_id
#         # assert result.tenant_id == tenant_id
#         # assert result.query == "What is the document content?"
#         # assert result.result == "Found content."
#         # assert result.status == "completed"

#         # Cleanup
#         await repo_query.delete(tenant_id, query_id)
#         await repo_chunk.delete(tenant_id, chunk_id)
#         await repo_doc.delete(tenant_id, doc_id)
