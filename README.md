# ⚖️ SME Legal Assistant

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue?logo=python" />
  <img src="https://img.shields.io/badge/FastAPI-0.111+-009688?logo=fastapi" />
  <img src="https://img.shields.io/badge/Streamlit-frontend-FF4B4B?logo=streamlit" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
</p>

An **AI-powered contract analysis assistant** built for **Small & Medium Enterprises (SMEs)** in India.  
This tool analyzes PDF/DOCX/TXT contracts, identifies risky clauses, provides clause-by-clause explanations,  
and generates **professional PDF/Markdown reports**.

---

## ✨ Features
- 📄 **Contract ingestion** (PDF, DOCX, TXT)
- 🔍 **Clause detection** (English & Hindi headings supported)
- ⚖️ **Risk analysis** using heuristics + optional LLM insights
- 📊 **Interactive dashboard** with risk distribution & charts
- 📑 **Exportable reports** (Markdown & styled PDF)
- 🌐 **REST API** (FastAPI) + **Frontend UI** (Streamlit)
- 🔒 **Privacy-first** → Contracts are processed locally

---

## 📂 Project Structure
legal-assistant/
│
├── backend/ # FastAPI backend
│ ├── main.py # API endpoints
│ ├── analysis.py # Contract analyzer
│ ├── rules.py # Clause rules & heuristics
│ ├── ingest.py # PDF/DOCX/TXT ingestion
│ ├── llm.py # LLM integration (Groq API)
│ ├── models.py # Pydantic models
│ └── tests/ # Unit tests
│
├── frontend/ # Streamlit frontend
│ └── app.py # UI dashboard
│
├── risks.json # Configurable risk weights
├── README.md # Project documentation
└── requirements.txt # Dependencies

---

git clone https://github.com/YOUR_USERNAME/legal-assistant.git
cd legal-assistant
2️⃣ Setup Backend
bash
Copy code
cd backend
python -m venv .venv
source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt

# run backend
uvicorn main:app --reload --port 8000
Backend will be live at: http://localhost:8000/docs

3️⃣ Setup Frontend
bash
Copy code
cd ../frontend
python -m venv .venv
source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt

# run frontend
streamlit run app.py
Frontend will be live at: http://localhost:8501

🐳 Docker (Optional)
Build & run with Docker Compose:

bash
Copy code
docker-compose up --build
📸 Screenshots (to add later)
📤 Upload page

📊 Dashboard with risk charts

📑 PDF Report

🧪 Testing
Run backend tests:

bash
Copy code
pytest backend/tests/
🔑 Environment Variables
Create a .env in backend/:

ini
Copy code
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
Without an API key, the app falls back to heuristic-only analysis.

🛠️ Tech Stack
Backend: FastAPI, Pydantic, ReportLab, pdfplumber, python-docx, spaCy

Frontend: Streamlit, Plotly

LLM (optional): Groq API (Llama 3.3)

Deployment-ready: Docker, GitHub Actions (future)

****🤝 Contributing
Fork the repo

Create a new branch (feature-x)

Commit changes

Open a Pull Request 🚀****

