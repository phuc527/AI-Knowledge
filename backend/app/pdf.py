import os
import uuid

import chromadb
import ollama
from fastapi import UploadFile
from pypdf import PdfReader


chroma_client = chromadb.PersistentClient(
    path="./chroma"
)

collection = chroma_client.get_or_create_collection(
    name="documents"
)


def split_text(text: str, chunk_size: int = 1000):
    chunks = []

    for start in range(0, len(text), chunk_size):
        chunk = text[start:start + chunk_size]

        if chunk.strip():
            chunks.append(chunk)

    return chunks


def create_embeddings(documents: list[str]):
    response = ollama.embed(
        model="nomic-embed-text",
        input=documents,
    )

    embeddings = response["embeddings"]

    print(
        f"Embedding dimension: {len(embeddings[0])}"
    )

    return embeddings


async def process_pdf(file: UploadFile):
    file_id = str(uuid.uuid4())

    file_path = f"uploads/{file_id}_{file.filename}"

    os.makedirs("uploads", exist_ok=True)

    with open(file_path, "wb") as output:
        output.write(await file.read())

    reader = PdfReader(file_path)

    documents = []
    metadatas = []
    ids = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if not text.strip():
            continue

        chunks = split_text(text)

        for chunk_index, chunk in enumerate(chunks):
            documents.append(chunk)

            metadatas.append({
                "file": file.filename,
                "page": page_number,
                "chunk": chunk_index,
            })

            ids.append(str(uuid.uuid4()))

    if not documents:
        return {
            "message": "PDF contains no readable text",
            "file": file.filename,
            "pages": len(reader.pages),
            "chunks": 0,
        }

    embeddings = create_embeddings(documents)

    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids,
    )

    return {
        "message": "PDF processed successfully",
        "file": file.filename,
        "pages": len(reader.pages),
        "chunks": len(documents),
        "embedding_dimension": len(embeddings[0]),
    }