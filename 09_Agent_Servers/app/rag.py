from __future__ import annotations

import os
from functools import lru_cache
from typing import Annotated

import tiktoken
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain_core.tools import tool
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"


def _tiktoken_len(text: str) -> int:
    return len(tiktoken.encoding_for_model("gpt-4o").encode(text))


@lru_cache(maxsize=1)
def _get_retriever():
    data_dir = os.environ.get("RAG_DATA_DIR", "data")

    try:
        documents = DirectoryLoader(
            data_dir, glob="**/*.pdf", loader_cls=PyMuPDFLoader
        ).load()
    except Exception:
        documents = []

    if not documents:
        return None

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=750, chunk_overlap=0, length_function=_tiktoken_len
    )
    chunks = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(
        model=os.environ.get("OPENAI_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL),
        openai_api_key=os.environ["OPENAI_API_KEY"],
    )
    vectorstore = QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        location=":memory:",
        collection_name="rag_collection",
    )
    return vectorstore.as_retriever()


@tool
def retrieve_information(
    query: Annotated[str, "query to ask the retrieve information tool"],
) -> str:
    """Retrieve information about feline health, including life stage care, nutrition, vaccinations, parasite control, behavior, diagnostics, and veterinary guidelines for cats."""
    retriever = _get_retriever()
    docs = retriever.invoke(query) if retriever else []
    if not docs:
        return "No relevant information found in the knowledge base."
    return "\n\n".join(doc.page_content for doc in docs)
