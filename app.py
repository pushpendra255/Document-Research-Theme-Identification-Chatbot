import streamlit as st
import os
from PyPDF2 import PdfReader
import requests

# Chatbot config
BOT_NAME = "📘 EduMentor – AI Chatbot"
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Ask Groq
def ask_groq(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are an assistant that gives short, relevant answers from Indian government PDFs and policies."},
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

# UI
st.set_page_config(page_title=BOT_NAME, layout="wide")
st.markdown(f"<h1 style='text-align:center;color:#3A7CA5'>{BOT_NAME}</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Ask questions related to uploaded PDFs or Indian policies</p>", unsafe_allow_html=True)
st.markdown("---")

# Upload
uploaded = st.file_uploader("📄 Upload your PDF(s)", type="pdf", accept_multiple_files=True)

# Ask
query = st.text_input("💬 Ask your question here:")

# Submit button
submit = st.button("🚀 Get Answer", use_container_width=True)

if submit and query:
    with st.spinner("Thinking..."):
        combined_text = "\n".join(extract_text(f) for f in uploaded) if uploaded else ""
        
        if combined_text.strip():
            prompt = f"Based on the following document, answer the question briefly:\n\n{combined_text[:10000]}\n\nQuestion: {query}"
            answer = ask_groq(prompt)
        else:
            answer = ask_groq(query)

        # Answer output
        st.markdown("### ✅ Answer")
        st.success(answer)
