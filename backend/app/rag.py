import chromadb
from openai import OpenAI

from app.config import OPENAI_API_KEY


client = OpenAI(api_key=OPENAI_API_KEY)

chroma_client = chromadb.PersistentClient(
    path="./chroma"
)

collection = chroma_client.get_or_create_collection(
    name="documents"
)


async def ask_question(question: str):
    results = collection.query(
        query_texts=[question],
        n_results=5,
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return {
            "answer": "I don't have enough information.",
            "sources": [],
        }

    context = "\n\n".join(documents)

    prompt = f"""
You are an AI assistant for answering questions about uploaded documents.

Use only the provided context.

If the answer cannot be found in the context,
say that you don't have enough information.

Context:
{context}

Question:
{question}
"""

    response = client.responses.create(
        model="gpt-5",
        input=prompt,
    )

    return {
        "answer": response.output_text,
        "sources": metadatas,
    }