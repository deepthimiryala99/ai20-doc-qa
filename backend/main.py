from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
import fitz

from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

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

Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

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

    if file.filename.endswith(".pdf"):
        extracted_text = extract_text_from_pdf(file_path)

    elif file.filename.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            extracted_text = f.read()

    documents = [Document(text=extracted_text)]

    index = VectorStoreIndex.from_documents(documents)

    return {
        "message": "File uploaded and indexed successfully",
        "filename": file.filename
    }


@app.post("/ask")
async def ask_question(request: QuestionRequest):
    global index

    if index is None:
        return {
            "answer": "Please upload a document first."
        }

    question = request.question.lower().strip()

    unrelated_words = ["hi", "hello", "hey"]

    if question in unrelated_words:
        return {
            "answer": "Please ask a question related to the uploaded document."
        }

    retriever = index.as_retriever(similarity_top_k=1)

    nodes = retriever.retrieve(request.question)

    if not nodes:
        return {
            "answer": "I don't know the answer based on the uploaded document."
        }

    text = nodes[0].text

    shortened_text = text[:700]

    return {
        "answer": shortened_text
    }