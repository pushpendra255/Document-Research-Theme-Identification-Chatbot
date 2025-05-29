import streamlit as st
import os
from PyPDF2 import PdfReader
import requests
import uuid

# CONFIG
BOT_NAME = "📚 EduMentor – AI Chatbot"
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# API CALL
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
    except:
        return "❌ API error occurred."

# EXTRACT TEXT
@st.cache_data(show_spinner=False)
def extract_text_and_citations(file):
    doc_id = f"DOC{str(uuid.uuid4())[:4].upper()}"
    try:
        reader = PdfReader(file)
        full_text = ""
        pages_info = []
        for i, page in enumerate(reader.pages):
            content = page.extract_text() or ""
            full_text += content + "\n"
            pages_info.append((i + 1, content))
        return doc_id, full_text, pages_info
    except:
        return None, "", []

# UI SETUP
st.set_page_config(page_title=BOT_NAME, layout="wide")
st.markdown(f"<h1 style='text-align:center;color:#3A7CA5'>{BOT_NAME}</h1>", unsafe_allow_html=True)
st.markdown("---")

uploaded = st.file_uploader("📄 Upload PDFs (optional)", type="pdf", accept_multiple_files=True)
query = st.text_input("💬 Ask your question here:")
submit = st.button("✍️ Get Answer", use_container_width=True)

if submit and query:
    with st.spinner("Generating response..."):
        doc_rows = []
        all_text = ""
        theme_doc_ids = []

        if uploaded:
            for file in uploaded:
                doc_id, full_text, pages = extract_text_and_citations(file)
                if query.lower() in full_text.lower():
                    theme_doc_ids.append(doc_id)
                    for page_num, content in pages:
                        if query.lower() in content.lower():
                            doc_rows.append({
                                "doc_id": doc_id,
                                "snippet": content.strip()[:180] + "...",
                                "citation": f"Page {page_num}"
                            })
                    all_text += full_text + "\n"

        # Answer
        if all_text:
            short_prompt = f"Answer the question briefly based only on this text:\n\n{all_text[:8000]}\n\nQ: {query}"
            answer = ask_groq(short_prompt)
        else:
            answer = ask_groq(query)

        # Display
        st.success("### ✅ Answer")
        st.markdown(f"<div style='background-color:#114B23;padding:15px;border-radius:10px;color:white'>{answer}</div>", unsafe_allow_html=True)

        # Presentation Section
        if doc_rows:
            st.markdown("---")
            st.markdown("### 📌 Presentation of Results:")

            # TABLE
            st.markdown("**Individual document responses:**")
            st.table({
                "Document ID": [r["doc_id"] for r in doc_rows],
                "Extracted Answer": [r["snippet"] for r in doc_rows],
                "Citation": [r["citation"] for r in doc_rows]
            })

            # SYNTHESIS
            st.markdown("**Final synthesized response with document references:**")
            st.info(f"**Theme 1 – Relevant Evidence**: Documents ({', '.join(theme_doc_ids)}) contain excerpts that support the answer to the question.")
            st.info("**Theme 2 – Citation Confidence**: Presented document snippets provide legal or policy-backed references.")

        else:
            st.markdown("<p style='color:gray;font-size:13px;'>No citations available since no PDF matched the query. Answer is generated from AI knowledge base.</p>", unsafe_allow_html=True)
