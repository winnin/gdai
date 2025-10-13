import asyncio

from gdai.temporal.conversational_llm.worker import main as main_conversational_llm_
from gdai.temporal.embedding_texts.worker import main as main_text_embedding
from gdai.temporal.extract_document.worker import main as main_extract_document
from gdai.temporal.search_on_documents.worker import main as main_search_on_documents
from gdai.temporal.upload_file.worker import main as main_upload_file


async def main():
    await asyncio.gather(
        main_conversational_llm_(),
        main_text_embedding(),
        main_extract_document(),
        main_search_on_documents(),
        main_upload_file(),
    )


if __name__ == "__main__":
    asyncio.run(main())
