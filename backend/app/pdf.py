import os
import uuid

import chromadb
from fastapi import UploadFile
from openai import OpenAI
from pypdf import PdfReader

from app.config import OPENAI_API_KEY


client = OpenAI(api_key=OPENAI_API_KEY)

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


async def process_pdf(file: UploadFile):
    file_id = str(uuid.uuid4())

    file_path = f"uploads/{file_id}_{file.filename}"

    os.makedirs("uploads", exist_ok=True)

    with open(file_path, "wb") as output:
        output.write(await file.read())

    reader = PdfReader(file_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if text.strip():
            pages.append({
                "page": page_number,
                "text": text,
            })

    documents = []
    metadatas = []
    ids = []

    for page in pages:
        chunks = split_text(page["text"])

        for chunk_index, chunk in enumerate(chunks):
            documents.append(chunk)

            metadatas.append({
                "file": file.filename,
                "page": page["page"],
                "chunk": chunk_index,
            })

            ids.append(str(uuid.uuid4()))

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
    )

    return {
        "message": "PDF processed successfully",
        "file": file.filename,
        "pages": len(pages),
        "chunks": len(documents),
    }