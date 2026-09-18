from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.pdf import process_pdf
from app.rag import ask_question


app = FastAPI(title="AI Knowledge API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    return await process_pdf(file)


@app.post("/chat")
async def chat(question: str):
    return await ask_question(question)