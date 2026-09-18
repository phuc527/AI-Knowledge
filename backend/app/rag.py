import chromadb
import ollama


chroma_client = chromadb.PersistentClient(
    path="./chroma"
)

collection = chroma_client.get_or_create_collection(
    name="documents"
)


def create_embedding(question: str):
    response = ollama.embed(
        model="nomic-embed-text",
        input=question,
    )

    embedding = response["embeddings"][0]

    print(
        f"Question embedding dimension: {len(embedding)}"
    )

    return embedding


async def ask_question(question: str):
    query_embedding = create_embedding(question)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5,
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return {
            "answer": "I don't have enough information.",
            "sources": [],
        }

    context = "\n\n".join(
        f"[Page {metadata['page']}]\n{document}"
        for document, metadata in zip(
            documents,
            metadatas
        )
    )

    prompt = f"""
You are an AI assistant for answering questions about uploaded documents.

Use ONLY the provided context.

If the answer cannot be found in the context,
say that you don't have enough information.

Context:
{context}

Question:
{question}

Answer:
"""

    response = ollama.generate(
        model="llama3.2",
        prompt=prompt,
    )

    return {
        "answer": response["response"],
        "sources": metadatas,
    }