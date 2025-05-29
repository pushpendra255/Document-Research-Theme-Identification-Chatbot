import streamlit as st
import os
from PyPDF2 import PdfReader
import requests

# Chatbot config
BOT_NAME = "📘 EduMentor – AI Chatbot"
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Ask Groq LLaMA-3
def ask_groq(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are an assistant that gives short and useful answers based on Indian policies and documents."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        res = requests.post(GROQ_API_URL, headers=headers, json=data)
        return res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"❌ API error: {e}"

# Extract text from PDF
def extract_text(file):
    try:
        return "".join(page.extract_text() or "" for page in PdfReader(file).pages)
    except:
        return ""

# UI Setup
st.set_page_config(page_title=BOT_NAME, layout="wide")
st.markdown(f"<h1 style='text-align:center;color:#3A7CA5'>{BOT_NAME}</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Ask questions about education policies or uploaded PDFs</p>", unsafe_allow_html=True)
st.markdown("---")

# Upload
uploaded = st.file_uploader("📄 Upload PDFs (optional)", type="pdf", accept_multiple_files=True)

# Ask
query = st.text_input("💬 Ask your question here:")

# Stylish button
submit = st.button("🚀 Get Answer", use_container_width=True)

# On click
if submit and query:
    with st.spinner("Thinking..."):
        all_text = "\n".join(extract_text(f) for f in uploaded) if uploaded else ""
        if query.lower() in all_text.lower():
            short_prompt = f"Give a short, clear answer to the question based on this text:\n\n{all_text[:8000]}\n\nQ: {query}"
            answer = ask_groq(short_prompt)
        else:
            answer = ask_groq(query)

        # Show final answer only
        st.markdown("### ✅ Answer")
        st.success(answer)
