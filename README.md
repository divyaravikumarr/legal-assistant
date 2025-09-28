⚖️ SME Legal Assistant
<p align="center"> <img src="https://img.shields.io/badge/Python-3.9%2B-blue?logo=python" /> <img src="https://img.shields.io/badge/FastAPI-0.111+-009688?logo=fastapi" /> <img src="https://img.shields.io/badge/Streamlit-frontend-FF4B4B?logo=streamlit" /> <img src="https://img.shields.io/badge/License-MIT-green" /> </p>

SME Legal Assistant is an AI-powered contract analysis tool designed for Small & Medium Enterprises (SMEs) in India.
It ingests contracts in multiple formats, detects risky clauses, provides plain-language explanations, and generates professional PDF/Markdown reports—helping business owners make informed decisions without needing deep legal expertise.

🚀 Highlights

📄 Upload PDF, DOCX, or TXT contracts

🔍 Detects clause headings (supports English & Hindi)

⚖️ Provides risk analysis (heuristics + optional LLM insights via Groq API)

📊 Interactive dashboard with charts & risk breakdown

📑 Generate exportable reports (styled PDF & Markdown)

🌐 REST API (FastAPI) + modern frontend (Streamlit)

🔒 Privacy-first → All processing is local

📂 Project Structure
legal-assistant/
│
├── backend/              # FastAPI backend
│   ├── main.py           # API endpoints
│   ├── analysis.py       # Contract analyzer
│   ├── rules.py          # Clause rules & heuristics
│   ├── ingest.py         # PDF/DOCX/TXT ingestion
│   ├── llm.py            # LLM integration (Groq API)
│   ├── models.py         # Pydantic models
│   └── tests/            # Unit tests
│
├── frontend/             # Streamlit frontend
│   └── app.py            # UI dashboard
│
├── risks.json            # Configurable risk weights
├── README.md             # Documentation
└── requirements.txt      # Dependencies

⚙️ Installation & Setup
1️⃣ Clone Repository
git clone https://github.com/YOUR_USERNAME/legal-assistant.git
cd legal-assistant

2️⃣ Backend Setup
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run backend
uvicorn main:app --reload --port 8000


📍 Backend live at: http://localhost:8000/docs

3️⃣ Frontend Setup
cd ../frontend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run frontend
streamlit run app.py


📍 Frontend live at: http://localhost:8501

🐳 Docker (Optional)

Run with Docker Compose:

docker-compose up --build

🧪 Testing

Run unit tests:

pytest backend/tests/

🔑 Environment Variables

Create a .env file inside backend/:

GROQ_API_KEY=your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile


👉 Without an API key, the system falls back to heuristic-only analysis.

🛠️ Tech Stack

Backend: FastAPI, Pydantic, ReportLab, pdfplumber, python-docx, spaCy

Frontend: Streamlit, Plotly

LLM (optional): Groq API (Llama 3.3)

DevOps: Docker, GitHub Actions (CI/CD planned)

📸 Screenshots (Coming Soon)

📤 Upload Page

📊 Risk Dashboard

📑 Exported PDF Report

🤝 Contributing

Fork the repository

Create a feature branch (feature-x)

Commit & push changes

Open a Pull Request 🚀

📜 License

This project is licensed under the MIT License – free to use & modify.
