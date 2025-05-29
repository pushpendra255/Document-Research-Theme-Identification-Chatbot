import streamlit as st
import os
from PyPDF2 import PdfReader
import requests
import re
import pandas as pd

# Configuration
BOT_NAME = "📘 EduMentor – AI Chatbot"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
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
            {"role": "system", "content": "You are an assistant that provides concise answers based on Indian policies and uploaded documents."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        res = requests.post(GROQ_API_URL, headers=headers, json=data)
        return res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"❌ API error: {e}"

# Cached PDF text extraction
@st.cache_data(show_spinner=False)
def extract_text_cached(file):
    reader = PdfReader(file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

# Precise citation extraction
def get_precise_citation(file, query):
    reader = PdfReader(file)
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if query.lower() in text.lower():
            return f"Page {page_num}"
    return "Not Found"

# Improved matching segments
def improved_match(text, query):
    matches = re.findall(rf"([^.]*{re.escape(query)}[^.]*)", text, flags=re.IGNORECASE)
    return matches[0].strip() if matches else "Relevant information found."

# UI Setup
st.set_page_config(page_title=BOT_NAME, layout="wide")
st.markdown(f"<h1 style='text-align:center;color:#3A7CA5'>{BOT_NAME}</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Ask questions related to Indian policies or your uploaded PDFs. Structured results appear below.</p>", unsafe_allow_html=True)
st.markdown("---")

# Upload PDFs
uploaded = st.file_uploader("📄 Upload PDFs (optional)", type="pdf", accept_multiple_files=True)

# Question input
example_q = "Example: What is the National Education Policy?"
query = st.text_input("🖋️ Ask your question here:", placeholder=example_q)
submit = st.button("✍️ Get Answer", use_container_width=True)

# Process
if submit and query:
    with st.spinner("Thinking..."):
        doc_table, doc_ids, joined_answers = [], [], ""

        if uploaded:
            for i, file in enumerate(uploaded):
                doc_id = f"DOC{i+1:03d}"
                text = extract_text_cached(file)
                if query.lower() in text.lower():
                    citation = get_precise_citation(file, query)
                    answer_text = improved_match(text, query)
                    doc_table.append({
                        "Document ID": doc_id,
                        "Document Name": file.name,
                        "Extracted Answer": answer_text,
                        "Citation": citation
                    })
                    doc_ids.append(doc_id)

            joined_answers = "\n".join([f"{d['Document ID']} ({d['Document Name']}, {d['Citation']}): {d['Extracted Answer']}" for d in doc_table])

        if doc_table:
            theme_prompt = (
                "Cluster the provided document answers into themes. "
                "Clearly mention each theme followed by related Document IDs in parentheses. "
                "Example format:\n"
                "Theme 1 – [Theme Name]: Documents (DOC001, DOC002)\n"
                "Theme 2 – [Another Theme]: Documents (DOC003)\n\n"
                f"Provided document answers:\n{joined_answers}\n\n"
                f"Question: {query}"
            )
            summary = ask_groq(theme_prompt)

            concise_prompt = (
                "Using only the provided document answers, give a concise and clear response. "
                "Explicitly reference Document IDs, Document Names, and exact citations (page numbers). "
                "Ensure the answer clearly indicates the source. Example format:\n"
                "\"According to DOC001 (DocumentName.pdf, Page 4), [extracted answer]...\"\n\n"
                f"Provided document answers:\n{joined_answers}\n\n"
                f"Question: {query}"
            )
            final_answer = ask_groq(concise_prompt)
        else:
            final_answer = ask_groq(query)
            summary = "No matching documents found; answer generated from external knowledge."

        # Answer
        st.markdown("### ✅ Final Answer")
        st.success(final_answer)

        # Presentation of Results
        if doc_table:
            st.markdown("---")
            st.markdown("### 📊 Presentation of Results:")

            df = pd.DataFrame(doc_table)[["Document ID", "Document Name", "Extracted Answer", "Citation"]]
            st.table(df)

            st.markdown("#### 💡 Synthesized Response (Themes):")
            st.info(summary)
