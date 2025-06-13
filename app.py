

   
import streamlit as st
import os
import tempfile
from PyPDF2 import PdfReader
import requests
import re
from sentence_transformers import SentenceTransformer
import faiss
import google.generativeai as genai

# ========== Configure Gemini ==========
genai.configure(api_key="AIzaSyBeoYwJuJSaOGyWbNwzgoGl8rb2OtctSN8")

# ========== Setup ==========
model = SentenceTransformer("all-MiniLM-L6-v2")
doc_index = faiss.IndexFlatL2(384)
doc_texts = []
doc_ids = []

# ========== PDF Extraction ==========
def extract_text(file):
    try:
        reader = PdfReader(file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except:
        return ""

# ========== Vector Storage ==========
def store_document(text, doc_id):
    doc_ids.append(doc_id)
    doc_texts.append(text)
    vec = model.encode([text])
    doc_index.add(vec)

# ========== Search ==========
def search_documents(query):
    q_vec = model.encode([query])
    D, I = doc_index.search(q_vec, k=3)
    return [doc_texts[i] for i in I[0] if i < len(doc_texts)]

# ========== Citation ==========
def get_citation(text, query):
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if query.lower() in line.lower():
            return f"Page {i//25 + 1}, Line {i%25 + 1}"
    return "Not Found"

# ========== Ask Gemini ==========
def ask_gemini(prompt):
    model = genai.GenerativeModel("gemini-pro")
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Gemini API error: {e}"

# ========== Streamlit UI ==========
st.set_page_config(page_title="EduMentor – Gemini Chatbot", layout="wide")
st.title("📘 EduMentor – Policy Research Chatbot (Gemini-Powered)")

uploaded_files = st.file_uploader("📄 Upload PDFs", type="pdf", accept_multiple_files=True)
query = st.text_input("🔍 Ask your question:", placeholder="Example: What is the National Education Policy?")
submit = st.button("✍️ Get Answer")

if submit and query:
    with st.spinner("Analyzing documents..."):
        matched_docs = []
        answer_table = []

        if uploaded_files:
            for i, file in enumerate(uploaded_files):
                doc_id = f"DOC{i+1:03d}"
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(file.read())
                    tmp_path = tmp.name
                text = extract_text(tmp_path)
                store_document(text, doc_id)

                if query.lower() in text.lower():
                    citation = get_citation(text, query)
                    snippet = re.findall(rf"(.{{0,100}}{re.escape(query)}.{{0,200}})", text, flags=re.IGNORECASE)
                    answer_text = snippet[0].strip() if snippet else "Relevant info found."
                    answer_table.append({
                        "Document ID": doc_id,
                        "Extracted Answer": answer_text,
                        "Citation": citation,
                        "Source File": file.name
                    })
                    matched_docs.append(f"{doc_id}: {answer_text}")

        if matched_docs:
            joined_answers = "\n".join(matched_docs)
            prompt = f"Answer the following based on document text:\n\n{joined_answers}\n\nQ: {query}"
            final_answer = ask_gemini(prompt)

            theme_prompt = (
                f"Identify themes from the document snippets below.\n"
                f"Use this format:\nTheme 1 – Description: Documents (DOC001, DOC002)\n\n{joined_answers}"
            )
            themes = ask_gemini(theme_prompt)
        else:
            final_answer = ask_gemini(query)
            themes = "No theme found."

        st.markdown("### ✅ Answer")
        st.success(final_answer)

        if matched_docs:
            import pandas as pd
            st.markdown("### 📊 Matching Document Results")
            st.dataframe(pd.DataFrame(answer_table), use_container_width=True)

        st.markdown("### 🧠 Theme Summary")
        st.info(themes)
