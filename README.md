# MediScript-AI-Project
MediScript AI is an AI-powered system designed to analyze medical prescriptions by reading uploaded photos, extracting drug information, checking for interactions across over 500,000 records, and providing bilingual explanations.
# 💊 MediScript AI
### Pakistan's First AI Prescription Analyzer
> **HackData V1 | GDGoC CUI Wah | April 2026**

---

## 🚀 Live Demo
- **Frontend:** [your-app.streamlit.app](https://your-app.streamlit.app)
- **Backend API:** [mediscript-backend.onrender.com/health](https://mediscript-backend.onrender.com/health)
- **API Docs:** [mediscript-backend.onrender.com/docs](https://mediscript-backend.onrender.com/docs)

---

## 🎯 Problem
70%+ of Pakistani patients **cannot understand** their own prescriptions:
- Handwritten Latin abbreviations (BID, TID, PRN, SOS)
- No bilingual explanation tools
- Dangerous drug-drug interactions go undetected
- 7,000+ deaths/year from medication errors (WHO)

## ✅ Solution
MediScript AI automatically:
1. **Reads** any prescription photo using Google Gemini Vision (Anti-Gravity)
2. **Checks** 500K+ FDA drug interactions via live government APIs
3. **Explains** everything in both **English** AND **Roman Urdu**
4. **Recommends** safer alternatives and lifestyle tips
5. **Generates** a downloadable PDF report

---

## 🏗️ Tech Stack (100% FREE — PKR 0)

| Layer | Technology |
|---|---|
| AI Vision | Google Gemini 1.5 Flash (Anti-Gravity) |
| Drug Interactions | OpenFDA FAERS API (500K+ records) |
| Drug Normalization | NLM RxNorm API (NIH) |
| Backend | FastAPI + Python + Uvicorn |
| Frontend | Streamlit (Python only) |
| Database | Supabase PostgreSQL |
| PDF Reports | ReportLab |
| Backend Hosting | Render.com |
| Frontend Hosting | Streamlit Community Cloud |
| CI/CD | GitHub Actions |

---

## 📁 Project Structure

```
mediscript-ai/
├── backend/
│   ├── main.py              # FastAPI server (all routes)
│   ├── gemini_service.py    # Gemini AI calls (Anti-Gravity)
│   ├── drug_checker.py      # Live FDA/NIH API interaction checker
│   └── supabase_client.py   # Database operations
├── frontend/
│   └── app.py               # Complete Streamlit UI
├── utils/
│   ├── image_processor.py   # PIL image enhancement
│   └── report_generator.py  # PDF generation
├── database/
│   └── schema.sql           # Supabase table definitions
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies
└── Procfile                 # Render deployment config
```

---

## ⚡ Quick Start

```bash
# 1. Clone
git clone https://github.com/hamzaali-712/MediScript-AI-Project.git
cd MediScript-AI-Project

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env
# Edit .env and add your Gemini API key and Supabase credentials

# 4. Run backend
uvicorn backend.main:app --reload --port 8000

# 5. Run frontend (new terminal)
streamlit run frontend/app.py
```

---

## 🔑 Getting API Keys (All Free)

| Service | URL | Time |
|---|---|---|
| Gemini API Key | [aistudio.google.com](https://aistudio.google.com) | 2 min |
| Supabase | [supabase.com](https://supabase.com) | 5 min |
| Render (deploy) | [render.com](https://render.com) | 3 min |
| Streamlit Cloud | [share.streamlit.io](https://share.streamlit.io) | 2 min |

---

## 👥 Team

| Name | Role |
|---|---|
| **Hamza Ali** | Project Idea & Lead |
| **Muhammad Umair Malik** | 
| **Shahzaib Shoaib Rathore** | 

---

## 📊 Impact
- 220M+ Urdu speakers can now understand their prescriptions
- 500,000+ FDA drug interaction records checked in real-time
- First bilingual (English + Roman Urdu) medical AI in Pakistan
- Zero cost to run — accessible for all

---

> *"Ab aapka nuskhaa samjhna asaan hai" — Now understanding your prescription is easy* 💊
