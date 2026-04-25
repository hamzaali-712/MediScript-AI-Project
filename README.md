# 💊 MediScript AI
### Pakistan's First AI Prescription Analyzer
> **HackData V1 | GDGoC CUI Wah | April 2026**

---

## 🚀 Live Demo
- **Frontend:** Deploy on [Streamlit Cloud](https://share.streamlit.io) — free
- **Backend API:** Deploy on [Render.com](https://render.com) — free
- **API Docs:** `https://your-backend.onrender.com/docs`

---

## 🎯 Problem
70%+ of Pakistani patients **cannot understand** their own prescriptions:
- Handwritten Latin abbreviations (BID, TID, PRN, SOS)
- No bilingual explanation available
- Dangerous drug-drug interactions go undetected
- 7,000+ deaths/year from medication errors (WHO estimate)

## ✅ Solution
MediScript AI automatically:
1. **Reads** any prescription photo via Google Gemini Vision
2. **Checks** 500K+ FDA drug interactions via live government APIs
3. **Explains** everything in **English + Roman Urdu**
4. **Recommends** safer alternatives and lifestyle tips
5. **Generates** a downloadable PDF report

---

## 🏗️ Tech Stack (100% FREE — PKR 0)

| Layer | Technology | Cost |
|---|---|---|
| AI Vision | Google Gemini 1.5 Flash | FREE |
| Drug Interactions | OpenFDA FAERS API (500K+ records) | FREE |
| Drug Normalization | NLM RxNorm API (NIH) | FREE |
| Drug Labels | DailyMed (NIH) | FREE |
| Backend | FastAPI + Python + Uvicorn | FREE |
| Frontend | Streamlit | FREE |
| Database | Supabase PostgreSQL | FREE |
| PDF Reports | ReportLab | FREE |
| Backend Hosting | Render.com | FREE |
| Frontend Hosting | Streamlit Community Cloud | FREE |
| **Total** | **PKR 0** | **100% FREE** |

---

## 📁 Project Structure

```
mediscript-ai/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI server + all routes
│   ├── gemini_service.py    # Gemini Vision AI calls
│   ├── drug_checker.py      # OpenFDA + RxNorm + DailyMed
│   └── supabase_client.py   # All database operations
├── utils/
│   ├── __init__.py
│   ├── image_processor.py   # PIL image enhancement
│   └── report_generator.py  # ReportLab PDF generation
├── database/
│   └── schema.sql           # Supabase table definitions
├── tests/
│   └── test_apis.py         # API health tests
├── .streamlit/
│   ├── config.toml          # Streamlit theme config
│   └── secrets.toml.example # Secrets template
├── app.py                   # Streamlit frontend
├── .env.example             # Environment variables template
├── .gitignore
├── Procfile                 # Render deployment
└── requirements.txt
```

---

## ⚡ Quick Start (Local)

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/MediScript-AI-Project.git
cd MediScript-AI-Project

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env and add your API keys (see below)

# 5. Set up Supabase database
# → Go to supabase.com → New Project
# → SQL Editor → Paste contents of database/schema.sql → Run

# 6. Run backend (Terminal 1)
uvicorn backend.main:app --reload --port 8000

# 7. Run frontend (Terminal 2)
streamlit run app.py

# 8. Open browser
# Frontend: http://localhost:8501
# Backend API docs: http://localhost:8000/docs
```

---

## 🔑 Getting API Keys (All Free)

| Service | Steps | Time |
|---|---|---|
| **Gemini API Key** | Go to [aistudio.google.com](https://aistudio.google.com) → Get API Key | 2 min |
| **Supabase** | Go to [supabase.com](https://supabase.com) → New Project → Get URL + Key | 5 min |
| **OpenFDA** (optional) | [open.fda.gov/apis](https://open.fda.gov/apis/authentication/) | 2 min |

---

## 🌐 Deployment Guide

### Backend → Render.com (Free)
1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. **Build Command:** `pip install -r requirements.txt`
5. **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
6. Add Environment Variables (from your `.env`):
   - `GEMINI_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `APP_ENV=production`
   - `ALLOWED_ORIGINS=https://your-app.streamlit.app`
7. Deploy! Get your URL: `https://mediscript-backend.onrender.com`

### Frontend → Streamlit Cloud (Free)
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo → Set **Main file:** `app.py`
4. Add Secret in Streamlit settings:
   ```
   BACKEND_URL = "https://mediscript-backend.onrender.com"
   ```
5. Deploy! Get your URL: `https://mediscript.streamlit.app`

---

## 🔧 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/auth/signup` | Register user |
| POST | `/auth/login` | Login user |
| GET | `/user/{id}` | Get user profile |
| **POST** | **`/analyze`** | **Main: analyze prescription** |
| GET | `/history` | Scan history |
| GET | `/scan/{id}` | Get specific scan |
| GET | `/analytics` | Drug analytics |
| GET | `/dashboard` | Dashboard stats |
| GET | `/drug-info/{name}` | Live drug info |

---

## 🧪 Test APIs

```bash
python tests/test_apis.py
```

---

## 👥 Team

| Role | Name |
|---|---|
| 💡 Project Idea & Lead | **Hamza Ali** |
| 👨‍💻 | **Muhammad Umair Malik** |
| 👨‍💻 | **Shahzaib Shoaib Rathore** |

---

## 📊 Impact
- 220M+ Urdu speakers can now understand their prescriptions
- 500,000+ FDA drug interaction records checked in real-time
- First bilingual (English + Roman Urdu) medical AI in Pakistan
- Zero infrastructure cost

---

> *"Ab aapka nuskhaa samjhna asaan hai"* — Now understanding your prescription is easy 💊
