import streamlit as st
import os
from PyPDF2 import PdfReader
import requests
import re
import pandas as pd

# ========== CONFIG ==========
BOT_NAME = "📘 EduMentor – AI Chatbot"
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ========== FUNCTIONS ==========
def ask_groq(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are an assistant that gives short, clear answers and summarizes themes from Indian policies and documents."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"❌ API error: {e}"

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

# ========== UI ==========
st.set_page_config(page_title=BOT_NAME, layout="wide")
st.markdown(f"<h1 style='text-align:center;color:#3A7CA5'>{BOT_NAME}</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Ask any questions or upload PDFs. Summary and results appear below.</p>", unsafe_allow_html=True)
st.markdown("---")

uploaded = st.file_uploader("📄 Upload PDFs (optional)", type="pdf", accept_multiple_files=True)
query = st.text_input("🖋️ Ask your question here:", placeholder="Example: What is the National Education Policy?")
submit = st.button("✍️ Get Answer", use_container_width=True)

# ========== PROCESS ==========
if submit and query:
    with st.spinner("Thinking..."):
        doc_table = []
        matched_content = []

        if uploaded:
            for i, file in enumerate(uploaded):
                doc_id = f"DOC{i+1:03d}"
                text = extract_text(file)
                if query.lower() in text.lower():
                    citation = get_citation(text, query)
                    match = re.findall(rf"(.{{0,100}}{re.escape(query)}.{{0,200}})", text, re.IGNORECASE)
                    extracted = match[0] if match else "Relevant content found."
                    doc_table.append({"Document ID": doc_id, "Extracted Answer": extracted.strip(), "Citation": citation})
                    matched_content.append(f"{doc_id}: {extracted.strip()}")

        # Final Answer (from Groq + document)
        if matched_content:
            answer = ask_groq(f"Based on the following info, give a short and direct answer:\n\n{matched_content}\n\nQ: {query}")
            theme_prompt = f"Group these document responses into themes with their document IDs:\n{matched_content}"
            themes = ask_groq(theme_prompt)
        else:
            answer = ask_groq(query)
            themes = "No theme found."

        # Show Answer
        st.markdown("### ✅ Answer")
        st.success(answer)

        if doc_table:
            st.markdown("### 📊 Presentation of Results:")
            df = pd.DataFrame(doc_table)
            st.dataframe(df, use_container_width=True)

            st.markdown("#### 🧠 Final synthesized response:")
            st.info(themes)
