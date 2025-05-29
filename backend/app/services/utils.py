import os
import fitz  # PyMuPDF
import nltk
import torch
import faiss
import numpy as np
from transformers import pipeline
from sentence_transformers import SentenceTransformer

nltk.download("punkt")

# Models
embedder = SentenceTransformer("all-MiniLM-L6-v2")
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# Storage
texts, files = [], []
index = None

def extract_text_from_pdf(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def chunk_text(text, chunk_size=300):
    from nltk.tokenize import sent_tokenize
    sentences = sent_tokenize(text)
    chunks, current_chunk = [], ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def index_pdfs(folder):
    global texts, files, index
    texts, files = [], []
    for filename in os.listdir(folder):
        if filename.endswith(".pdf"):
            path = os.path.join(folder, filename)
            raw = extract_text_from_pdf(path)
            for chunk in chunk_text(raw):
                texts.append(chunk)
                files.append(filename)
    vectors = embedder.encode(texts, convert_to_numpy=True)
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)

def search_answer(query, top_k=3):
    if not index:
        return "No documents indexed.", []
    
    query_embedding = embedder.encode([query])
    D, I = index.search(np.array(query_embedding), top_k)

    matched_chunks = [texts[i] for i in I[0] if i < len(texts)]
    sources = [files[i] for i in I[0] if i < len(files)]

    combined = " ".join(matched_chunks)[:1500]  # Truncate input

    try:
        summary = summarizer(combined, max_length=80, min_length=20, do_sample=False)[0]['summary_text']
    except:
        summary = combined[:300]

    return summary, sources
