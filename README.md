📘 EduMentor – AI Chatbot

EduMentor is an advanced question-answering chatbot that intelligently reads uploaded PDF documents and gives concise, context-aware responses. If the answer isn’t found within the PDFs, it smartly falls back to Groq’s LLaMA 3 model for external knowledge.

> ✅ Built with speed, clarity, and user-friendly design in mind.




---

🌐 Live Demo

👉 Try it now:
https://edumentor-theme-chatbot.streamlit.app/


---

🔍 Key Features

🔹 Upload PDFs – Drag, drop, and ask from multiple documents

🔹 Smart Q&A – Extracts precise answers from document content

🔹 Fallback AI – Uses Groq’s LLaMA 3 when no answer is found in files

🔹 Citation Tracking – Pinpoints source page and line

🔹 Theme Identification – Clusters document responses by themes

🔹 Streamlit Interface – Clean, fast, and interactive UI



---

🧠 Sample Q&A Output

✅ Answer:
“National Education Policy 2020 aims to transform India’s education system by promoting holistic, flexible, and multidisciplinary learning.”

📊 Presentation of Results:

Document ID	Extracted Answer	Citation	Source File

DOC001	NEP 2020 focuses on holistic development...	Page 4, Line 6	NEP_policy.pdf
DOC002	The document outlines flexible learning options for students.	Page 2, Line 10	School_Reforms.pdf


🧠 Final Synthesized Themes:

Theme 1 – Policy Direction: Documents (DOC001, DOC002) describe the vision and strategy of NEP.

Theme 2 – Implementation: DOC002 highlights steps toward rollout and adoption.



---

📁 Folder Structure

├── app.py                  # Streamlit app
├── backend/
│   └── data/               # Store uploaded PDFs
├── requirements.txt        # Python dependencies


---

⚙️ Tech Stack

Tool	Purpose

🐍 Python	Core scripting
📚 PyPDF2	PDF reading
🔗 Requests	API communication
🧠 Groq API	LLaMA 3-based intelligent responses
📊 pandas	Display and organize tabular outputs
🚀 Streamlit	Web app UI and deployment



---

🚀 Getting Started Locally

1. Clone the repository:



git clone https://github.com/pushpendra255/Document-Research-Theme-Identification-Chatbot
cd Document-Research-Theme-Identification-Chatbot

2. Install dependencies:



pip install -r requirements.txt

3. Run the Streamlit app:



streamlit run app.py

4. Upload your PDFs and start asking questions!




---

🙌 Credits

Made with 💡 using:

Groq’s LLaMA 3

Streamlit

PyPDF2


