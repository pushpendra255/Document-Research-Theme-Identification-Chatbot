import streamlit as st
import os
from PyPDF2 import PdfReader
import requests

# 💡 CHATBOT CONFIG
BOT_NAME = "📘 EduMentor – AI Chatbot"
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# 🌐 Send query to Groq LLaMA-3
def get_groq_response(query):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that gives short and useful answers about education policies, laws, and public documents."},
            {"role": "user", "content": query}
        ]
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"⚠️ Groq API Error: {response.status_code} - {response.text}"

# 🌟 UI SETUP
st.set_page_config(page_title=BOT_NAME, page_icon="📘", layout="wide")
st.markdown(f"<h1 style='color:#3A7CA5'>{BOT_NAME}</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

query = st.text_input("🔎 Ask a question about the documents or any topic:")

# 📂 Load from backend/data (limit and show size)
@st.cache_resource
def load_folder_pdfs(folder_path, max_files=15):
    docs = []
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]
    files = sorted(files)[:max_files]  # ✅ Load only first few for speed
    for filename in files:
        filepath = os.path.join(folder_path, filename)
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        if size_mb > 20:
            st.warning(f"⚠️ Skipped {filename} (too big: {size_mb:.1f} MB)")
            continue
        st.write(f"📄 Loading: {filename} ({size_mb:.2f} MB)")
        try:
            reader = PdfReader(filepath)
            content = "".join(page.extract_text() or "" for page in reader.pages)
            docs.append({"filename": filename, "content": content})
        except Exception as e:
            st.error(f"❌ Could not read {filename}: {e}")
    return docs

# 📤 Upload via UI
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

# 📦 Load PDFs from backend/data once
with st.spinner("📂 Loading from backend/data..."):
    if "documents" not in st.session_state:
        st.session_state.documents = load_folder_pdfs("backend/data", max_files=15)

all_docs = st.session_state.documents + uploaded_docs

# 🔍 Search or Fallback
if query:
    matched = []
    for doc in all_docs:
        if query.lower() in doc["content"].lower():
            matched.append(doc["filename"])

    if matched:
        st.success("✅ Found answer in the following PDFs:")
        st.markdown("\n".join([f"• 📄 **{m}**" for m in matched]))
    else:
        st.info("🧠 No direct match found. Asking Groq (LLaMA-3)...")
        answer = get_groq_response(query)
        st.markdown(f"<div style='background-color:#f0f4f8;padding:15px;border-radius:10px;border-left:5px solid #3A7CA5'><b>🤖 Answer:</b><br>{answer}</div>", unsafe_allow_html=True)
