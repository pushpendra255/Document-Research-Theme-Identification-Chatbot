import streamlit as st
import os
from PyPDF2 import PdfReader
import requests

# === CONFIG ===
BOT_NAME = "\U0001F4D8 EduMentor – AI Chatbot"
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# === GROQ API ===
def get_groq_response(query):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that summarizes relevant document information and combines it with public knowledge to answer questions clearly and shortly."},
            {"role": "user", "content": query}
        ]
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"\u26a0\ufe0f Groq API Error: {response.status_code} - {response.text}"

# === UI ===
st.set_page_config(page_title=BOT_NAME, page_icon="\U0001F4D8", layout="wide")
st.markdown(f"<h1 style='color:#3A7CA5;text-align:center'>{BOT_NAME}</h1>", unsafe_allow_html=True)
st.markdown("""
    <style>
        .centered-box {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2em;
        }
        .stButton>button {
            background-color: #3A7CA5;
            color: white;
            padding: 10px 25px;
            font-size: 16px;
            border-radius: 8px;
            border: none;
            margin-top: 1em;
        }
    </style>
""", unsafe_allow_html=True)

query = st.text_input("\ud83d\udd0e Ask a question about the documents or any topic:")

# Add a centered Submit button
with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submit = st.button("\ud83d\udcac Submit")

# === PDF LOADERS ===
@st.cache_resource
def load_folder_pdfs(folder_path, max_files=15):
    docs = []
    files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")])[:max_files]
    for filename in files:
        path = os.path.join(folder_path, filename)
        size_mb = os.path.getsize(path) / (1024 * 1024)
        if size_mb > 20:
            continue
        try:
            reader = PdfReader(path)
            text = " ".join(page.extract_text() or "" for page in reader.pages)
            docs.append({"filename": filename, "content": text})
        except:
            pass
    return docs

# Upload UI
uploaded_files = st.file_uploader("\ud83d\udccc Upload additional PDF(s)", type="pdf", accept_multiple_files=True)
uploaded_docs = []
if uploaded_files:
    for file in uploaded_files:
        try:
            reader = PdfReader(file)
            content = " ".join(page.extract_text() or "" for page in reader.pages)
            uploaded_docs.append({"filename": file.name, "content": content})
        except:
            pass

# Load backend/data
if "documents" not in st.session_state:
    st.session_state.documents = load_folder_pdfs("backend/data")

all_docs = st.session_state.documents + uploaded_docs

# === Matching & Groq Combo ===
def search_documents(query, docs):
    query_words = set(query.lower().split())
    relevant_texts = []
    for doc in docs:
        content_words = set(doc["content"].lower().split())
        if len(query_words & content_words) > 3:
            snippet = doc["content"][:1000].replace("\n", " ")
            relevant_texts.append(snippet)
    return "\n".join(relevant_texts[:3])

# === Answer Flow ===
if submit and query:
    doc_context = search_documents(query, all_docs)
    if doc_context:
        st.success("\u2705 Relevant content found in documents. Combining with Groq...")
        combined_query = f"Answer this question using the following document excerpts:\n\n{doc_context}\n\nQuestion: {query}"
    else:
        st.info("\ud83e\uddd0 No PDF matched well, asking Groq directly...")
        combined_query = query

    final_answer = get_groq_response(combined_query)
    st.markdown("<h4>\ud83e\uddd1\u200d\ud83d\udcd6 Answer:</h4>", unsafe_allow_html=True)
    st.write(final_answer)
