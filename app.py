import streamlit as st
import os
from PyPDF2 import PdfReader
import requests
import uuid
import re

# Basic Config
BOT_NAME = "📘 EduMentor – AI Chatbot"
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Function to query Groq

def ask_groq(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are an assistant that gives concise, citation-based answers from uploaded PDFs. If info isn't found, answer using general knowledge."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        res = requests.post(GROQ_API_URL, headers=headers, json=data)
        return res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"❌ API error: {e}"

# PDF Text Extractor

def extract_text(file):
    try:
        return "\n".join(page.extract_text() or "" for page in PdfReader(file).pages)
    except:
        return ""

# Streamlit UI Setup
st.set_page_config(page_title=BOT_NAME, layout="wide")
st.markdown(f"<h1 style='text-align:center;color:#3A7CA5'>{BOT_NAME}</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Ask questions from your uploaded PDFs or general topics</p>", unsafe_allow_html=True)
st.markdown("---")

# File Upload
uploaded = st.file_uploader("📄 Upload PDFs", type="pdf", accept_multiple_files=True)
query = st.text_input("💬 Ask your question here:")
submit = st.button("🚀 Get Answer", use_container_width=True)

# On Submit
if submit and query:
    with st.spinner("Thinking..."):
        # Extract and tag text from PDFs
        results = []
        combined_text = ""
        if uploaded:
            for file in uploaded:
                doc_id = f"DOC{str(uuid.uuid4())[:4]}"
                text = extract_text(file)
                if not text.strip():
                    continue
                short_prompt = f"Give a short, useful answer to this question based on the document:\n\n{text[:8000]}\n\nQ: {query}"
                ans = ask_groq(short_prompt)
                # Simple citation extract (you can improve this logic)
                page_match = re.search(r'Page\s(\d+)', ans)
                citation = f"Page {page_match.group(1)}" if page_match else "-"
                results.append((doc_id, ans, citation))
                combined_text += f"[{doc_id}] {ans}\n"

        # Synthesized answer
        final_prompt = f"Summarize this info and group into themes with clear citations:\n\n{combined_text}\n\nQ: {query}"
        summary = ask_groq(final_prompt)

        # Display Answer
        st.markdown("### ✅ Answer")
        st.success(summary)

        # Table Format
        if results:
            st.markdown("---")
            st.markdown("### 📊 Presentation of Results")
            st.markdown("**Individual document responses:**")
            st.table({
                "Document ID": [r[0] for r in results],
                "Extracted Answer": [r[1] for r in results],
                "Citation": [r[2] for r in results]
            })
            st.markdown("**Final Synthesized Themes with Citations:**")
            st.info(summary)
