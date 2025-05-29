import streamlit as st
import os
from PyPDF2 import PdfReader
import requests
import re
import uuid
import pandas as pd

# Config
BOT_NAME = "\U0001F4D8 EduMentor – AI Chatbot"
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# 🧠 Ask Groq API
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

# 📖 Extract text

def extract_text(file):
    try:
        return "\n".join(page.extract_text() or "" for page in PdfReader(file).pages)
    except:
        return ""

def get_citation(text, query):
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if query.lower() in line.lower():
            return f"Page {i//25 + 1}, Line {i%25 + 1}"
    return "Not Found"

# 🌐 UI Setup
st.set_page_config(page_title=BOT_NAME, layout="wide")
st.markdown(f"<h1 style='text-align:center;color:#3A7CA5'>{BOT_NAME}</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Ask any questions or uploaded PDFs. Summary and results appear below.</p>", unsafe_allow_html=True)
st.markdown("---")

# 📂 Upload Section
uploaded = st.file_uploader("📄 Upload PDFs (optional)", type="pdf", accept_multiple_files=True)

# 💬 Question Input
example_q = "Example: What is the national education policy?"
query = st.text_input("🖋️ Ask your question here:", placeholder=example_q)
submit = st.button("✍️ Get Answer", use_container_width=True)

# 🚀 Submit
if submit and query:
    with st.spinner("Thinking..."):
        doc_table = []
        doc_ids = []
        matched_content = []

        if uploaded:
            for i, file in enumerate(uploaded):
                doc_id = f"DOC{i+1:03d}"
                text = extract_text(file)
                if query.lower() in text.lower():
                    citation = get_citation(text, query)
                    match_segment = re.findall(rf"(.{{0,100}}{re.escape(query)}.{{0,200}})", text, flags=re.IGNORECASE)
                    answer_text = match_segment[0].strip() if match_segment else "Relevant info found."
                    doc_table.append({"Document ID": doc_id, "Extracted Answer": answer_text, "Citation": citation})
                    doc_ids.append(doc_id)
                    matched_content.append(answer_text)

        if doc_table:
            theme_prompt = f"Summarize and cluster this into themes with document IDs:\n{matched_content}\n\nQuestion: {query}"
            summary = ask_groq(theme_prompt)
            answer = ask_groq(f"Give a short summary based on this:\n{matched_content}\n\nQuestion: {query}")
        else:
            answer = ask_groq(query)
            summary = "No documents matched."

        # ✅ Show Answer
        st.markdown("### ✅ Answer")
        st.success(answer)

        # 📊 Presentation
        if doc_table:
            st.markdown("---")
            st.markdown("### 📊 Presentation of Results:")
            df = pd.DataFrame(doc_table)
            st.dataframe(df, use_container_width=True)

            st.markdown("#### 🧠 Final synthesized response:")
            st.info(summary)
