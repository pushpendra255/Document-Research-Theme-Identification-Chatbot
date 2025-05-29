import streamlit as st
import os
from PyPDF2 import PdfReader
import requests

# ---------------------------- CONFIG -----------------------------------
BOT_NAME = "📘 EduMentor – AI Chatbot"
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ------------------------ LLM FALLBACK -------------------------------
def ask_groq(query):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Give short, clear answers using available public documents like policies, laws, and education schemes."},
            {"role": "user", "content": query}
        ]
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return f"❌ Groq API Error: {response.status_code}"

# ------------------------ PDF LOADER -------------------------------
@st.cache_resource
def load_pdfs(folder="backend/data", limit=15):
    docs = []
    files = sorted([f for f in os.listdir(folder) if f.endswith(".pdf")])[:limit]
    for file in files:
        path = os.path.join(folder, file)
        try:
            reader = PdfReader(path)
            text = "".join(page.extract_text() or "" for page in reader.pages)
            docs.append({"name": file, "content": text})
        except Exception as e:
            st.warning(f"❌ Couldn't read {file}: {e}")
    return docs

# ------------------------ PDF SEARCH -------------------------------
def search_pdfs(query, docs):
    matches = []
    for doc in docs:
        if query.lower() in doc["content"].lower():
            matches.append(doc)
    return matches

# ------------------------ STREAMLIT UI -------------------------------
st.set_page_config(page_title=BOT_NAME, page_icon="📘", layout="wide")
st.markdown(f"<h1 style='text-align:center; color:#3A7CA5'>{BOT_NAME}</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

with st.form("chat_form"):
    query = st.text_input("🔍 Ask a question about the documents or any topic:")
    submitted = st.form_submit_button("🚀 Submit", use_container_width=True)

# ------------------------ FILE UPLOAD -------------------------------
uploaded_docs = []
uploaded_files = st.file_uploader("📎 Upload additional PDF(s)", type="pdf", accept_multiple_files=True)
if uploaded_files:
    for file in uploaded_files:
        try:
            reader = PdfReader(file)
            text = "".join(page.extract_text() or "" for page in reader.pages)
            uploaded_docs.append({"name": file.name, "content": text})
        except Exception as e:
            st.warning(f"❌ Couldn't read {file.name}: {e}")

# ------------------------ LOAD & RESPOND -------------------------------
if submitted and query:
    with st.spinner("🔍 Searching..."):
        if "docs" not in st.session_state:
            st.session_state.docs = load_pdfs()
        all_docs = st.session_state.docs + uploaded_docs
        matched = search_pdfs(query, all_docs)

        if matched:
            st.success("✅ Relevant content found in the following PDFs:")
            for doc in matched:
                st.markdown(f"📄 **{doc['name']}**")
            # Summarize using matched documents
            combined = "\n".join([doc["content"] for doc in matched])[:8000]
            prompt = f"Based on the following documents, give a short and clear answer to:\n\n{query}\n\nDocuments:\n{combined}"
            final_answer = ask_groq(prompt)
        else:
            st.info("🤖 No match found in documents. Asking Groq directly...")
            final_answer = ask_groq(query)

        st.markdown(f"### 🧠 Answer:\n{final_answer}")
