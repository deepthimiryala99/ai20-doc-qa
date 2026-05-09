from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
import fitz
import re

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

document_text = ""


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
    global document_text

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if file.filename.lower().endswith(".pdf"):
        document_text = extract_text_from_pdf(file_path)

    elif file.filename.lower().endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            document_text = f.read()

    else:
        return {
            "message": "Only PDF and TXT files are supported.",
            "filename": file.filename,
        }

    if not document_text.strip():
        return {
            "message": "Could not extract text from this file.",
            "filename": file.filename,
        }

    return {
        "message": "File uploaded and processed successfully",
        "filename": file.filename,
    }


@app.post("/ask")
async def ask_question(request: QuestionRequest):
    global document_text

    if not document_text.strip():
        return {"answer": "Please upload a document first."}

    question = request.question.lower().strip()
    text_lower = document_text.lower()

    if question in ["hi", "hello", "hey"]:
        return {"answer": "Please ask a question related to the uploaded document."}

    if "whose" in question or "name" in question:
        lines = [line.strip() for line in document_text.split("\n") if line.strip()]
        return {"answer": lines[0] if lines else "I don't know based on the document."}

    if "experience" in question or "years" in question:
        match = re.search(r"(\d+\+?\s+years)", document_text, re.IGNORECASE)
        if match:
            return {"answer": f"She has {match.group(1)} of experience."}

    if "role" in question or "position" in question:
        if "customer support analyst" in text_lower:
            return {"answer": "Her recent role is Customer Support Analyst."}
        if "technical support analyst" in text_lower:
            return {"answer": "Her recent role is Technical Support Analyst."}
        if "business analyst" in text_lower:
            return {"answer": "Her recent role is Business Analyst."}

    sentences = re.split(r"(?<=[.!?])\s+", document_text)
    clean_answer = " ".join(sentences[:3]).strip()

    if not clean_answer:
        clean_answer = "I don't know the answer based on the uploaded document."

    return {"answer": clean_answer}