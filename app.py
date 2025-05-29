import streamlit as st
import os
from PyPDF2 import PdfReader
import requests
import re
import pandas as pd

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
        return f"\n❌ API error: {e}"

# Extract text with tracking
def extract_text(file, doc_id):
    try:
        reader = PdfReader(file)
        content = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                content.append({
                    "doc_id": doc_id,
                    "page": i + 1,
                    "text": text
                })
        return content
    except:
        return []

# Search with relevance
def search_text(query, extracted):
    matches = []
    for entry in extracted:
        if query.lower() in entry["text"].lower():
            snippet = entry["text"][:300].replace("\n", " ")
            para = get_para_number(entry["text"], query)
            matches.append({
                "Document ID": entry["doc_id"],
                "Extracted Answer": snippet.strip(),
                "Citation": f"Page {entry['page']}, Para {para}"
            })
    return matches

# Approximate para detection
def get_para_number(text, query):
    paras = text.split("\n")
    for i, para in enumerate(paras):
        if query.lower() in para.lower():
            return i + 1
    return "-"

# UI setup
st.set_page_config(page_title=BOT_NAME, layout="wide")
st.markdown(f"<h1 style='text-align:center;color:#3A7CA5'>{BOT_NAME}</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Ask questions about National Education Policy or any PDF content below.</p>", unsafe_allow_html=True)
st.markdown("---")

uploaded = st.file_uploader("\U0001F4C4 Upload PDFs (optional)", type="pdf", accept_multiple_files=True)
st.markdown("<br>", unsafe_allow_html=True)

query = st.text_input("\U0001F4AC Ask your question here:", placeholder="e.g., What is the National Education Policy?")
submit = st.button("\u2708 Get Answer", use_container_width=True)

if submit and query:
    with st.spinner("\U0001F9D0 Thinking..."):
        all_text = []
        if uploaded:
            for idx, file in enumerate(uploaded):
                doc_id = f"DOC{idx+1:03}"
                text = extract_text(file, doc_id)
                all_text.extend(text)

        results = search_text(query, all_text) if all_text else []

        if results:
            top_text = "\n\n".join([f"{r['Extracted Answer']} ({r['Citation']})" for r in results])
            prompt = f"Based on these snippets, answer shortly:\n\n{top_text}\n\nQ: {query}"
            answer = ask_groq(prompt)
        else:
            answer = ask_groq(query)

        st.markdown("### ✅ Answer")
        st.success(answer)

        if results:
            st.markdown("---")
            st.markdown("### 📊 Presentation of Results:")

            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)

            doc_ids = sorted(set(r["Document ID"] for r in results))
            st.markdown("**\n\n**")
            themes = [
                f"**Theme 1** – Extracted Insights: Documents ({', '.join(doc_ids)}) contain relevant policy discussions.",
                f"**Theme 2** – Document Sources: Each document supports different policy aspects through identified paragraphs."
            ]
            for t in themes:
                st.markdown(t)
