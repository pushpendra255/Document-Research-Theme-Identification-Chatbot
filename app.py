import streamlit as st
import os
from PyPDF2 import PdfReader
import requests
import re
import pandas as pd

BOT_NAME = "\U0001F4D8 EduMentor – AI Chatbot"
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Call LLaMA-3 API
def ask_groq(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You extract short answers with citations and summarize themes from government PDFs."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        res = requests.post(GROQ_API_URL, headers=headers, json=data)
        return res.json()["choices"][0]["message"]["content"].strip()
    except:
        return "❌ Failed to generate answer."

# Extract PDF text
def extract_text(file):
    try:
        return "\n".join([page.extract_text() or "" for page in PdfReader(file).pages])
    except:
        return ""

# Citation pattern
def extract_citations(text):
    paras = text.split("\n")
    matches = []
    for i, para in enumerate(paras):
        if len(para.strip()) > 30:
            matches.append((i+1, para.strip()))
    return matches[:2]  # take first 2 strong lines

# UI
st.set_page_config(page_title=BOT_NAME, layout="wide")
st.markdown(f"<h1 style='text-align:center;color:#3A7CA5'>{BOT_NAME}</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Ask questions based on uploaded PDFs. Summary and results appear below.</p>", unsafe_allow_html=True)
st.markdown("---")

uploaded = st.file_uploader("\U0001F4C4 Upload PDFs (optional)", type="pdf", accept_multiple_files=True)
query = st.text_input("\U0001F4AC Ask your question here:")
submit = st.button("\u2708\ufe0f Get Answer", use_container_width=True)

if submit and query:
    with st.spinner("Analyzing PDFs and generating response..."):
        all_text = ""
        extracted = []
        for i, file in enumerate(uploaded):
            doc_id = f"DOC{i+1:03}"
            text = extract_text(file)
            citation_lines = extract_citations(text)
            short_prompt = f"Answer this based only on the content below:\n{text[:6000]}\n\nQ: {query}"
            answer = ask_groq(short_prompt)
            citation_text = f"Page {citation_lines[0][0]}, Para {citation_lines[0][1][:40]}..." if citation_lines else "N/A"
            extracted.append({"Document ID": doc_id, "Extracted Answer": answer, "Citation": citation_text})
            all_text += f"\n[{doc_id}] {text}"

        final_prompt = f"Summarize the key themes in short bullet points from the following content and include Document IDs in parentheses:\n{all_text}\n\nQ: {query}"
        final_summary = ask_groq(final_prompt)

        st.markdown("### \u2705 Answer")
        overall = ask_groq(query)
        st.success(overall)

        if extracted:
            st.markdown("---")
            st.markdown("### \ud83d\udcca Presentation of Results")
            df = pd.DataFrame(extracted)
            st.markdown("**\u2022 Individual document responses in tabular format:**")
            st.dataframe(df, use_container_width=True)
            st.markdown("**\u2022 Final synthesized response with citations:**")
            st.info(final_summary)
