import streamlit as st
import os
from PyPDF2 import PdfReader
import requests

# === CONFIG ===
BOT_NAME = "📘 EduMentor – AI Chatbot"
GROQ_API_KEY = "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"  # Keep this key
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# === Groq API ===
def get_groq_response(query):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that gives short and relevant answers based on uploaded documents or general knowledge."},
            {"role": "user", "content": query}
        ]
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"⚠️ Groq API Error: {response.status_code} - {response.text}"

# === UI ===
st.set_page_config(page_title=BOT_NAME, page_icon="📘", layout="wide")
st.markdown(f"<h1 style='color:#3A7CA5'>{BOT_NAME}</h1>", unsafe_allow_html=True)
st.markdown("Ask questions about National Education Policy or any PDF content below.", unsafe_allow_html=True)
st.divider()

query = st.text_input("🔎 Ask a question about the documents or any topic:")
submit = st.button("💬 Submit")

# === PDF LOADERS ===
@st.cache_resource
def load_folder_pdfs(folder_path, max_files=15):
    docs = []
    files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")])[:max_files]
    for filename in files:
        path = os.path.join(folder_path, filename)
        size_mb = os.path.getsize(path) / (1024 * 1024)
        if size_mb > 20:
            st.warning(f"⚠️ Skipped {filename} (too big: {size_mb:.1f} MB)")
            continue
        st.write(f"📄 Loading: {filename} ({size_mb:.2f} MB)")
        try:
            reader = PdfReader(path)
            text = "".join(page.extract_text() or "" for page in reader.pages)
            docs.append({"filename": filename, "content": text})
        except Exception as e:
            st.error(f"❌ Could not read {filename}: {e}")
    return docs

# Upload UI
uploaded_files = st.file_uploader("📎 Upload additional PDF(s)", type="pdf", accept_multiple_files=True)
uploaded_docs = []
if uploaded_files:
    for file in uploaded_files:
        try:
            reader = PdfReader(file)
            content = "".join(page.extract_text() or "" for page in reader.pages)
            uploaded_docs.append({"filename": file.name, "content": content})
        except Exception as e:
            st.error(f"❌ Could not read {file.name}: {e}")

# Load backend/data
with st.spinner("📂 Loading from backend/data..."):
    if "documents" not in st.session_state:
        st.session_state.documents = load_folder_pdfs("backend/data")

all_docs = st.session_state.documents + uploaded_docs

# === MATCHING & ANSWERING ===
def search_documents(query, docs):
    query_words = set(query.lower().split())
    results = []
    for doc in docs:
        words = set(doc["content"].lower().split())
        overlap = query_words & words
        if len(overlap) > 3:  # Match threshold
            snippet = doc["content"][:500].replace("\n", " ")
            results.append({"filename": doc["filename"], "snippet": snippet})
    return results

# === Answer Flow ===
if submit and query:
    matches = search_documents(query, all_docs)

    if matches:
        st.success("✅ Relevant content found in the following PDFs:")
        for m in matches:
            st.markdown(f"**📄 {m['filename']}**")
            st.code(m["snippet"][:500] + " ...", language="text")
    else:
        st.info("🧠 No match found in PDFs. Asking Groq (LLaMA-3)...")
        answer = get_groq_response(query)
        st.markdown("**🤖 Groq LLaMA Answer:**")
        st.write(answer)
