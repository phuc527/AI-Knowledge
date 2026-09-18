# AI Knowledge Base — Local RAG

A simple AI Knowledge Base project built with **FastAPI, ChromaDB, Ollama, and React**.

The application allows users to:

- Upload PDF documents
- Extract text from PDF
- Split documents into chunks
- Generate embeddings locally with Ollama
- Store embeddings in ChromaDB
- Ask questions about uploaded documents
- Retrieve relevant document chunks
- Generate answers using a local LLM

No OpenAI API key is required.

---

## Architecture

```text
                    ┌──────────────────┐
                    │      React       │
                    │   Chat + Upload  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     FastAPI      │
                    └────────┬─────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
        Upload PDF                    Ask Question
              │                             │
              ▼                             ▼
           pypdf                       Embedding
              │                             │
              ▼                             ▼
         Chunking                 Ollama Embedding
              │                    nomic-embed-text
              ▼                             │
      Ollama Embedding                       ▼
      nomic-embed-text                   ChromaDB
              │                             │
              ▼                             ▼
          ChromaDB                    Top 5 Chunks
                                            │
                                            ▼
                                         Prompt
                                            │
                                            ▼
                                      Ollama LLM
                                        llama3.2
                                            │
                                            ▼
                                         Answer
```

---

# Tech Stack

## Backend

- Python
- FastAPI
- Uvicorn
- pypdf
- ChromaDB
- Ollama

## AI

### LLM

```text
llama3.2
```

Used to generate answers.

### Embedding Model

```text
nomic-embed-text
```

Used to convert document text and questions into vectors.

The embedding model returns vectors with:

```text
768 dimensions
```

The same embedding model must be used when indexing documents and querying questions.

## Database

```text
ChromaDB
```

Used as the vector database.

---

# Project Structure

```text
ai-knowledge/
│
├── backend/
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── pdf.py
│   │   └── rag.py
│   │
│   ├── uploads/
│   │
│   ├── chroma/
│   │
│   ├── requirements.txt
│   └── ...
│
├── frontend/
│   └── ...
│
└── README.md
```

---

# Requirements

Before running the project, install:

- Python 3.11+
- Ollama
- Node.js
- Git

Check Python:

```bash
python --version
```

Check Node:

```bash
node --version
```

Check Ollama:

```bash
ollama --version
```

---

# 1. Install Ollama Models

Pull the embedding model:

```bash
ollama pull nomic-embed-text
```

Pull the LLM:

```bash
ollama pull llama3.2
```

Check installed models:

```bash
ollama list
```

Expected:

```text
NAME
llama3.2
nomic-embed-text
```

---

# 2. Start Ollama

On Windows, Ollama normally runs as a background service.

Test:

```bash
ollama list
```

You can also test the LLM directly:

```bash
ollama run llama3.2
```

Then ask:

```text
What is React?
```

If Ollama responds, the LLM is ready.

Exit:

```text
/bye
```

---

# 3. Backend Setup

Go to backend:

```bash
cd backend
```

Create virtual environment:

```bash
python -m venv .venv
```

Activate on Windows:

```powershell
.venv\Scripts\activate
```

Activate on Git Bash:

```bash
source .venv/Scripts/activate
```

---

# 4. Install Python Dependencies

Create `requirements.txt`:

```txt
fastapi
uvicorn[standard]
python-multipart
pypdf
chromadb
ollama
```

Install:

```bash
pip install -r requirements.txt
```

---

# 5. Start FastAPI

Run:

```bash
uvicorn app.main:app --reload
```

Expected:

```text
Uvicorn running on http://127.0.0.1:8000
```

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

---

# 6. Upload PDF

The upload endpoint receives a PDF file.

Example:

```http
POST /upload
```

Flow:

```text
PDF
 ↓
Save file
 ↓
pypdf
 ↓
Extract text
 ↓
Split into chunks
 ↓
Ollama
 ↓
nomic-embed-text
 ↓
768-dimensional vectors
 ↓
ChromaDB
```

Example response:

```json
{
  "message": "PDF processed successfully",
  "file": "ai-demo.pdf",
  "pages": 3,
  "chunks": 8,
  "embedding_dimension": 768
}
```

---

# 7. Ask Questions

Example:

```http
POST /ask
```

Request:

```json
{
  "question": "What is this document about?"
}
```

Flow:

```text
Question
   ↓
nomic-embed-text
   ↓
Question vector
   ↓
ChromaDB
   ↓
Similarity Search
   ↓
Top 5 relevant chunks
   ↓
Prompt
   ↓
llama3.2
   ↓
Answer
```

Example response:

```json
{
  "answer": "The document explains...",
  "sources": [
    {
      "file": "ai-demo.pdf",
      "page": 1,
      "chunk": 0
    }
  ]
}
```

---

# 8. RAG Process

This project implements the following RAG pipeline:

## Step 1 — Load

Read the uploaded PDF using `pypdf`.

```python
reader = PdfReader(file_path)
```

---

## Step 2 — Split

Split extracted text into chunks.

```python
def split_text(text: str, chunk_size: int = 1000):
    chunks = []

    for start in range(0, len(text), chunk_size):
        chunk = text[start:start + chunk_size]

        if chunk.strip():
            chunks.append(chunk)

    return chunks
```

---

## Step 3 — Embed

Generate embeddings using:

```text
nomic-embed-text
```

Example:

```python
response = ollama.embed(
    model="nomic-embed-text",
    input=documents,
)
```

---

## Step 4 — Store

Store documents and vectors in ChromaDB:

```python
collection.add(
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas,
    ids=ids,
)
```

---

## Step 5 — Retrieve

When the user asks a question:

```python
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5,
)
```

The system retrieves the five most relevant chunks.

---

## Step 6 — Generate

The retrieved chunks are added to the prompt:

```text
Context:
[Page 1]
...

[Page 2]
...

Question:
...
```

Then Ollama generates the answer:

```python
response = ollama.generate(
    model="llama3.2",
    prompt=prompt,
)
```

---

# 9. Important: Embedding Dimension

The project uses:

```text
nomic-embed-text
```

which produces:

```text
768 dimensions
```

ChromaDB must use the same dimension for all vectors in a collection.

For example:

```text
Document embedding
        ↓
768

Question embedding
        ↓
768

ChromaDB
        ↓
Compatible
```

Do not mix embedding models with different dimensions.

For example:

```text
Old model
384 dimensions

nomic-embed-text
768 dimensions
```

This causes:

```text
InvalidArgumentError:
Collection expecting embedding with dimension of 384,
got 768
```

---

# 10. Fix ChromaDB Dimension Errors

If you previously created the ChromaDB collection using another embedding model, delete the old database.

Stop FastAPI:

```text
Ctrl + C
```

Delete:

```text
backend/chroma/
```

PowerShell:

```powershell
Remove-Item -Recurse -Force .\chroma
```

Git Bash:

```bash
rm -rf chroma
```

Start FastAPI again:

```bash
uvicorn app.main:app --reload
```

Then upload the PDF again.

---

# 11. Environment Variables

This project does not require:

```text
OPENAI_API_KEY
```

The AI runs locally through Ollama.

Therefore, you do not need:

```env
OPENAI_API_KEY=...
```

The main AI components are:

```text
Ollama
├── llama3.2
└── nomic-embed-text
```

---

# 12. Local AI Architecture

The application can run without calling an external AI API:

```text
Your Computer
│
├── FastAPI
│
├── ChromaDB
│
└── Ollama
    │
    ├── llama3.2
    │
    └── nomic-embed-text
```

This provides:

- No OpenAI API key
- No OpenAI API cost
- Local document processing
- Local embeddings
- Local LLM inference

---

# 13. Development Workflow

Recommended development order:

```text
Day 1
 │
 ├── Upload PDF
 │
 ├── Extract text
 │
 ├── Chunking
 │
 ├── Embedding
 │
 ├── ChromaDB
 │
 ├── RAG
 │
 ├── Ollama
 │
 └── React Chat
```

---

# 14. Example Questions

After uploading a PDF, try:

```text
What is this document about?
```

```text
Summarize the document.
```

```text
What are the main topics?
```

```text
What does page 2 explain?
```

```text
What are the important requirements?
```

The assistant should answer based only on retrieved document context.

If the information is not available:

```text
I don't have enough information.
```

---

# 15. Common Problems

## Ollama command not found

```text
bash: ollama: command not found
```

Check from PowerShell:

```powershell
ollama --version
```

If Ollama is installed on Windows but Git Bash cannot find it, restart the terminal or configure the Ollama executable in PATH.

---

## Model not found

Example:

```text
model "llama3.2" not found
```

Run:

```bash
ollama pull llama3.2
```

For embeddings:

```bash
ollama pull nomic-embed-text
```

---

## Chroma dimension mismatch

Example:

```text
Collection expecting embedding with dimension of 384,
got 768
```

Delete:

```text
chroma/
```

Then re-upload the documents.

---

## PDF has no text

Some PDFs are scanned images.

`pypdf` cannot directly extract text from image-only PDFs.

Current version supports:

```text
Text PDF
   ↓
pypdf
   ↓
Text
```

OCR support can be added later:

```text
Scanned PDF
   ↓
OCR
   ↓
Text
   ↓
RAG
```

---

# 16. Future Improvements

Possible next steps:

### Authentication

```text
JWT
Login
Register
User-specific documents
```

### Better Chunking

Instead of fixed 1000-character chunks:

```text
Recursive Chunking
Semantic Chunking
Overlap
```

### Better Vector Search

```text
Vector Search
+
Keyword Search
+
Hybrid Search
```

### Source Citations

Return:

```text
Answer
+
PDF filename
+
Page number
+
Relevant chunk
```

### Streaming

Stream Ollama responses to React:

```text
Ollama
   ↓
FastAPI
   ↓
SSE / WebSocket
   ↓
React
```

### Docker

Containerize:

```text
React
FastAPI
ChromaDB
Ollama
```

### Production

Possible production architecture:

```text
                    Internet
                       │
                       ▼
                    Nginx
                       │
              ┌────────┴────────┐
              ▼                 ▼
           React             FastAPI
                                │
                   ┌────────────┼────────────┐
                   ▼            ▼            ▼
                ChromaDB      Ollama       Redis
                                              │
                                           Celery
```

---

# 17. Goal of the Project

This project demonstrates the fundamentals of a local AI application:

```text
PDF
 ↓
Document Processing
 ↓
Chunking
 ↓
Embedding
 ↓
Vector Database
 ↓
Retrieval
 ↓
Prompt Engineering
 ↓
Local LLM
 ↓
AI Answer
```

It is a simple foundation for building:

- AI Knowledge Base
- Internal company chatbot
- PDF Chatbot
- Documentation assistant
- Customer support assistant
- RAG-based applications

---

# License

For learning and interview preparation purposes.
