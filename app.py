import streamlit as st
import os
from PyPDF2 import PdfReader
import requests
import re
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import torch

# ------------------ Configuration ------------------
BOT_NAME = "\U0001F4D8 EduMentor – AI Chatbot"
GROQ_API_KEY = "2y3S8C3iwcu7aWuliNTXvf8g8C6_69LmBCwm3cY9hF3c2jijw"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

model = SentenceTransformer("all-MiniLM-L6-v2")

# ------------------ Helper Functions ------------------
def ask_groq(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are an assistant that gives short and useful answers based on Indian policies and uploaded PDFs."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        res = requests.post(GROQ_API_URL, headers=headers, json=data)
        return res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"❌ API error: {e}"

def extract_text_with_pages(file):
    reader = PdfReader(file)
    texts = []
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        texts.append((page_num + 1, text))
    return texts

def semantic_match(query, texts, threshold=0.5):
    matches = []
    query_emb = model.encode(query, convert_to_tensor=True)
    for doc_id, (page_num, page_text) in enumerate(texts):
        sentences = page_text.split('. ')
        for i, sent in enumerate(sentences):
            if sent.strip():
                score = util.cos_sim(query_emb, model.encode(sent, convert_to_tensor=True)).item()
                if score >= threshold:
                    match_segment = f"...{sent.strip()}..."
                    matches.append((doc_id + 1, page_num, i + 1, match_segment))
    return matches

# ------------------ Streamlit UI ------------------
st.set_page_config(page_title=BOT_NAME, layout="wide")
st.markdown(f"<h1 style='text-align:center;color:#3A7CA5'>{BOT_NAME}</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Ask any questions or upload PDFs. Summary and results appear below.</p>", unsafe_allow_html=True)
st.markdown("---")

uploaded = st.file_uploader("📄 Upload PDFs (optional)", type="pdf", accept_multiple_files=True)
query = st.text_input("🔋 Ask your question here:", placeholder="Example: What is the National Education Policy?")
submit = st.button("✍️ Get Answer", use_container_width=True)

# ------------------ Main Logic ------------------
if submit and query:
    with st.spinner("Thinking..."):
        doc_table = []
        matched_content = []

        if uploaded:
            for i, file in enumerate(uploaded):
                doc_id = f"DOC{i+1:03d}"
                texts = extract_text_with_pages(file)
                matches = semantic_match(query, texts)
                if matches:
                    page, _, line, segment = matches[0]  # Take first match only
                    citation = f"Page {page}, Line {line}"
                    doc_table.append({
                        "Document ID": doc_id,
                        "Extracted Answer": segment,
                        "Citation": citation,
                        "Source File": file.name
                    })
                    matched_content.append(f"{doc_id}: {segment}")

        if doc_table:
            joined_answers = "\n".join([f"{d['Document ID']} – {d['Extracted Answer']}" for d in doc_table])[:3000]  # truncate

            concise_prompt = (
                f"Answer this question in short using the text below:\n\n{joined_answers}\n\nQ: {query}"
            )
            final_answer = ask_groq(concise_prompt)

            theme_prompt = (
                f"From the following document snippets, identify key themes clearly.\n"
                f"Use the format 'Theme 1 – Description: Documents (DOC001, DOC002)'.\n\n"
                f"{joined_answers}\n\nIf no clear themes found, respond with 'No theme found.'"
            )
            theme_summary = ask_groq(theme_prompt)

        else:
            final_answer = ask_groq(query)
            theme_summary = "No theme found."

        # ------------------ Display Results ------------------
        st.markdown("### ✅ Answer")
        st.success(final_answer)

        if doc_table:
            st.markdown("---")
            st.markdown("### 📊 Presentation of Results:")
            df = pd.DataFrame(doc_table)[["Document ID", "Extracted Answer", "Citation", "Source File"]]
            st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False).encode()
            st.download_button("⬇️ Download Results", data=csv, file_name="results.csv", mime="text/csv")

            st.markdown("#### 🧠 Final synthesized response (Themes):")
            if not theme_summary.lower().startswith("theme"):
                theme_summary = "No theme found."
            st.info(theme_summary)
        else:
            st.markdown("---")
            st.markdown("<p style='color:gray;font-size:13px;'>No document matches found. Answer is generated using AI knowledge only.</p>", unsafe_allow_html=True)
            st.markdown("#### 🧠 Final synthesized response (Themes):")
            st.info(theme_summary)
