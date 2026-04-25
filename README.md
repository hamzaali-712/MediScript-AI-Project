---
title: MediScript API
emoji: 💊
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# 💊 MediScript AI
### Pakistan's First AI Prescription Analyzer
> **HackData V1 | GDGoC CUI Wah | April 2026**

---

## 🚀 Live Demo
- **Frontend:** [mediscript-app.hf.space](https://hamzalali1234-mediscript-app.hf.space)
- **Backend API:** [mediscript-api.hf.space](https://hamzalali1234-mediscript-api.hf.space)
- **API Docs:** [mediscript-api.hf.space/docs](https://hamzalali1234-mediscript-api.hf.space/docs)

---

## 🎯 Problem

70%+ of Pakistani patients **cannot understand** their own prescriptions:
- Handwritten Latin abbreviations (BID, TID, PRN, SOS) go misunderstood
- No bilingual explanation available at point of care
- Dangerous drug-drug interactions go undetected
- 7,000+ deaths/year from medication errors (WHO estimate)
- 220M+ Urdu speakers have no bilingual medical AI solution

---

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
| Backend Hosting | Hugging Face Spaces | FREE |
| Frontend Hosting | Hugging Face Spaces | FREE |
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
├── Dockerfile               # HF Spaces deployment
├── app.py                   # Streamlit frontend
├── .env.example             # Environment variables template
├── .gitignore
└── requirements.txt
```

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

## ⚡ Local Setup

```bash
# 1. Clone
git clone https://github.com/hamzaali-712/MediScript-AI-Project.git
cd MediScript-AI-Project

# 2. Virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Add your API keys in .env

# 5. Run backend (Terminal 1)
uvicorn backend.main:app --reload --port 8000

# 6. Run frontend (Terminal 2)
streamlit run app.py
```

---

## 🔑 API Keys (All Free)

| Service | Link | Time |
|---|---|---|
| **Gemini API** | [aistudio.google.com](https://aistudio.google.com) | 2 min |
| **Supabase** | [supabase.com](https://supabase.com) | 5 min |
| **OpenFDA** | [open.fda.gov/apis](https://open.fda.gov/apis/authentication/) | 2 min |

---

## 📊 Impact

- 220M+ Urdu speakers can now understand their prescriptions
- 500,000+ FDA drug interaction records checked in real-time
- First bilingual (English + Roman Urdu) medical AI in Pakistan
- Zero infrastructure cost — PKR 0

---

## 👥 Team

| Role | Name |
|---|---|
| 💡 Project Idea & Lead | **Hamza Ali** |
| 👨‍💻 Full Stack Developer | **Muhammad Umair Malik** |
| 👨‍💻 Full Stack Developer | **Shahzaib Shoaib Rathore** |

---

> *"Ab aapka nuskhaa samjhna asaan hai"* — Now understanding your prescription is easy 💊
