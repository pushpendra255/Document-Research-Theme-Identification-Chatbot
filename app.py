import streamlit as st
import os
from PyPDF2 import PdfReader
import requests

# ✅ CONFIG
BOT_NAME = "📘 EduMentor – AI Chatbot"
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# 🤖 Groq API fallback
def ask_groq(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are an educational assistant. Give short, clear answers from government/public documents."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        res = requests.post(GROQ_API_URL, headers=headers, json=payload)
        return res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"❌ Error calling Groq API: {e}"

# 📄 Load & clean PDFs
def load_text_from_pdf(file):
    try:
        reader = PdfReader(file)
        return "".join(page.extract_text() or "" for page in reader.pages)
    except:
        return ""

# 🧠 Search for relevant PDFs
def find_relevant_text(query, docs):
    combined = ""
    for doc in docs:
        if query.lower() in doc.lower():
            combined += doc + "\n"
    return combined

# 🖼️ Streamlit UI
st.set_page_config(page_title=BOT_NAME, page_icon="📘", layout="wide")
st.markdown(f"<h1 style='text-align:center; color:#3A7CA5'>{BOT_NAME}</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# 📎 Upload & ask
uploaded_files = st.file_uploader("📎 Upload PDF(s)", type="pdf", accept_multiple_files=True)
query = st.text_input("💬 Ask your question here:")

if st.button("🚀 Submit", use_container_width=True) and query:
    with st.spinner("Thinking..."):
        texts = [load_text_from_pdf(f) for f in uploaded_files]
        all_text = "\n".join(texts)
        match_text = find_relevant_text(query, texts)

        if match_text.strip():
            # Ask Groq to summarize based on matched text
            prompt = f"Answer this question briefly based on the following document:\n\n{match_text[:8000]}\n\nQuestion: {query}"
            answer = ask_groq(prompt)
        else:
            # No match, ask directly
            answer = ask_groq(query)

        st.markdown(f"### ✅ Answer:\n{answer}")
