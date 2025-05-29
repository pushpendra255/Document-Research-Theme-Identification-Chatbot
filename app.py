import streamlit as st
import os
from PyPDF2 import PdfReader
import requests
import re
import pandas as pd

# Configuration
BOT_NAME = "📘 EduMentor – AI Chatbot"
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Ask Groq API
def ask_groq(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are an assistant that gives short and useful answers based on Indian policies and uploaded PDF documents."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        res = requests.post(GROQ_API_URL, headers=headers, json=data)
        return res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"❌ API error: {e}"

# Extract PDF text
def extract_text(file):
    try:
        return "\n".join(page.extract_text() or "" for page in PdfReader(file).pages)
    except:
        return ""

# Get citation from text line index
def get_citation(text, query):
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if query.lower() in line.lower():
            return f"Page {i//25 + 1}, Line {i%25 + 1}"
    return "Not Found"

# UI
st.set_page_config(page_title=BOT_NAME, layout="wide")
st.markdown(f"<h1 style='text-align:center;color:#3A7CA5'>{BOT_NAME}</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Ask any questions or uploaded PDFs. Summary and results appear below.</p>", unsafe_allow_html=True)
st.markdown("---")

uploaded = st.file_uploader("📄 Upload PDFs (optional)", type="pdf", accept_multiple_files=True)

example_q = "Example: What is the National Education Policy?"
query = st.text_input("🖋️ Ask your question here:", placeholder=example_q)
submit = st.button("✍️ Get Answer", use_container_width=True)

if submit and query:
    with st.spinner("Thinking..."):
        doc_table = []
        matched_content = []

        if uploaded:
            for i, file in enumerate(uploaded):
                doc_id = f"DOC{i+1:03d}"
                file_name = file.name
                text = extract_text(file)
                if query.lower() in text.lower():
                    citation = get_citation(text, query)
                    match = re.findall(rf"(.{{0,100}}{re.escape(query)}.{{0,200}})", text, flags=re.IGNORECASE)
                    snippet = match[0].strip() if match else "Match found, but context not clear."
                    doc_table.append({
                        "Document ID": doc_id,
                        "PDF Name": file_name,
                        "Extracted Answer": snippet,
                        "Citation": citation
                    })
                    matched_content.append(f"{doc_id} ({file_name}): {snippet}")

        # Generate answer
        if doc_table:
            joined_answers = "\n".join(matched_content)
            summary_prompt = (
                f"Based on the following PDF content, provide a short summary to answer the question:\n\n"
                f"{joined_answers}\n\nQ: {query}"
            )
            theme_prompt = (
                f"Analyze and extract 1-2 themes based on this PDF content. Each theme should mention involved Document IDs and context:\n\n"
                f"{joined_answers}"
            )
            final_answer = ask_groq(summary_prompt)
            theme_summary = ask_groq(theme_prompt)
        else:
            final_answer = ask_groq(query)
            theme_summary = "No theme found."

        # Display Answer
        st.markdown("### ✅ Answer")
        st.success(final_answer)

        # Results Table
        if doc_table:
            st.markdown("---")
            st.markdown("### 📊 Presentation of Results")
            df = pd.DataFrame(doc_table)
            st.dataframe(df, use_container_width=True)

        # Theme Summary
        st.markdown("#### 🧠 Final synthesized response")
        st.info(theme_summary)
