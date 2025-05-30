📘 EduMentor – AI Chatbot

EduMentor is an advanced question-answering chatbot that intelligently reads PDF documents and gives concise, context-aware responses. If the answer isn’t found in the uploaded documents, it gracefully falls back to Groq’s LLaMA 3 model for external knowledge.

> ✅ Built with speed, clarity, and user-friendly design in mind.



🌐 Live Demo

👉 Try it now: 

https://edumentor-theme-chatbot.streamlit.app/


🔍 Key Features

🔹 Upload PDFs – Drag, drop, and ask from multiple documents

🔹 Smart Q&A – Extracts precise answers from your files

🔹 Fallback AI – Groq’s LLaMA 3 API gives answers when no match found

🔹 Citation Tracking – See exactly which page & line the answer came from

🔹 Themes Identification – Groups results under relevant themes

🔹 Streamlit App – Fast, intuitive interface for all users




🧠 Sample Q&A Output

✅ Answer:
National Education Policy 2020 aims to transform India’s education system by promoting holistic, flexible, and multidisciplinary learning.

📊 Presentation of Results:

Document ID	Extracted Answer	Citation	Source File

DOC001	NEP 2020 focuses on holistic development...	Page 4, Line 6	NEP_policy.pdf
DOC002	The document outlines flexible learning options for students.	Page 2, Line 10	School_Reforms.pdf


🧠 Final Synthesized Themes:

Theme 1 – Policy Direction: Documents (DOC001, DOC002) describe the vision and strategy of NEP.

Theme 2 – Implementation: DOC002 highlights steps toward rollout and adoption.




📁 Folder Structure

├── app.py                  # Streamlit app
├── backend/
│   └── data/               # Store uploaded PDFs
├── requirements.txt        # Required Python packages



⚙️ Tech Stack

Tool	Purpose

🐍 Python	Core scripting
📚 PyPDF2	PDF reading
🔗 Requests	API communication
🧠 Groq API	AI reasoning with LLaMA 3
📊 pandas	Tabular output
🚀 Streamlit	Frontend & web deployment




🚀 Getting Started Locally

1. Clone the repository

git clone https://github.com/yourusername/edumentor-chatbot.git
cd edumentor-chatbot


2. Install dependencies

pip install -r requirements.txt


3. Run the app

streamlit run app.py


4. Upload your PDFs and start chatting!





🙌 Credits

Made with 💡 using:

Groq’s LLaMA 3

Streamlit

PyPDF2

