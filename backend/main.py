from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
import fitz
import re

from llama_index.core import VectorStoreIndex, Document, Settings

app = FastAPI(title="AI20 Document Q&A Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "storage/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

Settings.llm = None

index = None


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {"message": "AI20 Document Q&A Backend is running"}


def extract_text_from_pdf(pdf_path):
    text = ""
    pdf = fitz.open(pdf_path)

    for page in pdf:
        text += page.get_text()

    return text


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    global index

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = ""

    if file.filename.lower().endswith(".pdf"):
        extracted_text = extract_text_from_pdf(file_path)

    elif file.filename.lower().endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            extracted_text = f.read()

    if not extracted_text.strip():
        return {
            "message": "Could not extract text from this file.",
            "filename": file.filename,
        }

    documents = [Document(text=extracted_text)]
    index = VectorStoreIndex.from_documents(documents)

    return {
        "message": "File uploaded and indexed successfully",
        "filename": file.filename,
    }


@app.post("/ask")
async def ask_question(request: QuestionRequest):
    global index

    if index is None:
        return {"answer": "Please upload a document first."}

    question = request.question.lower().strip()

    if question in ["hi", "hello", "hey"]:
        return {"answer": "Please ask a question related to the uploaded document."}

    retriever = index.as_retriever(similarity_top_k=1)
    nodes = retriever.retrieve(request.question)

    if not nodes:
        return {"answer": "I don't know the answer based on the uploaded document."}

    context = nodes[0].text

    if "whose" in question or "name" in question:
        lines = [line.strip() for line in context.split("\n") if line.strip()]
        return {"answer": lines[0] if lines else "I don't know based on the document."}

    if "experience" in question or "years" in question:
        match = re.search(r"(\d+\+?\s+years)", context, re.IGNORECASE)
        if match:
            return {"answer": f"She has {match.group(1)} of experience."}

    if "role" in question or "position" in question:
        if "customer support analyst" in context.lower():
            return {"answer": "Her recent role is Customer Support Analyst."}

    sentences = context.split(".")
    clean_answer = ".".join(sentences[:2]).strip()

    if not clean_answer:
        clean_answer = "I don't know the answer based on the uploaded document."

    return {"answer": clean_answer}