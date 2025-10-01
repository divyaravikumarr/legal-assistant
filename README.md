---

# ⚖️ SME Legal Assistant

<p align="center">  
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue?logo=python" />  
  <img src="https://img.shields.io/badge/FastAPI-0.111+-009688?logo=fastapi" />  
  <img src="https://img.shields.io/badge/Streamlit-frontend-FF4B4B?logo=streamlit" />  
  <img src="https://img.shields.io/badge/License-MIT-green" />  
</p>  

---

### 📝 Overview

**SME Legal Assistant** is an AI-powered **contract analysis tool** built for **Small & Medium Enterprises (SMEs) in India**.

It ingests contracts in multiple formats, detects risky clauses, explains them in plain language, and generates professional **PDF/Markdown reports** — helping business owners make **informed decisions** without needing deep legal expertise.

---

### 🚀 Features

* 📄 Upload contracts in **PDF, DOCX, TXT**
* 🔍 **Clause detection** (supports English & Hindi)
* ⚖️ **Risk analysis** → Heuristics + (optional) LLM via Groq API
* 📊 **Interactive dashboard** with risk breakdown & charts
* 📑 Export reports → **Styled PDF / Markdown**
* 🌐 **REST API** (FastAPI backend) + **modern Streamlit frontend**
* 🔒 **Privacy-first**: all processing runs locally

---

### ⚙️ Installation & Setup

#### 1️⃣ Clone Repository

```bash
git clone https://github.com/divyaravikumarr/legal-assistant.git
cd legal-assistant
```

#### 2️⃣ Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run backend
uvicorn main:app --reload --port 8000
```

📍 Backend Live: [http://localhost:8000/docs](http://localhost:8000/docs)

#### 3️⃣ Frontend Setup

```bash
cd ../frontend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run frontend
streamlit run app.py
```

📍 Frontend Live: [http://localhost:8501](http://localhost:8501)

---

### 🐳 Run with Docker (Optional)

```bash
docker-compose up --build
```

---

### 🧪 Testing

Run unit tests with:

```bash
pytest backend/tests/
```

---

### 🔑 Environment Variables

Create a `.env` file inside **backend/**:

```ini
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

👉 Without an API key, the system falls back to **heuristic-only analysis**.

---

### 🛠️ Tech Stack

**Backend** → FastAPI, Pydantic, ReportLab, pdfplumber, python-docx, spaCy
**Frontend** → Streamlit, Plotly
**LLM (optional)** → Groq API (Llama 3.3)
**DevOps** → Docker, GitHub Actions (CI/CD planned)

---



### 🤝 Contributing

1. Fork the repository
2. Create a new feature branch → `feature-xyz`
3. Commit & push your changes
4. Open a Pull Request 🚀

---

### 📜 License

This project is licensed under the **MIT License** – free to use & modify.

---


