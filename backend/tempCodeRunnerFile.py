"""
MediScript AI — FastAPI Backend Server
HackData V1 | GDGoC CUI Wah
Team: Hamza Ali | Muhammad Umair Malik | Shahzaib Shoaib Rathore

Routes:
  GET  /health               Health check
  POST /auth/signup          Register new user
  POST /auth/login           Login user
  GET  /user/{user_id}       Get user profile
  POST /analyze              Analyze prescription image  ← MAIN endpoint
  GET  /history              Get scan history
  GET  /scan/{id}            Get specific scan
  GET  /analytics            Drug analytics
  GET  /dashboard            Dashboard stats
  GET  /user/{id}/activity   User activity log
  GET  /drug-info/{name}     Live drug info from FDA/NIH
"""


import os
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional

from backend.gemini_service import (
    extract_drugs,
    explain_prescription,
    get_recommendations,
    double_check_prescription,
)
from backend.drug_checker import check_interactions_live, get_drug_info_live
from backend.supabase_client import (
    create_user,
    login_user,
    get_user_by_id,
    save_scan,
    get_history,
    get_scan_by_id,
    get_analytics,
    get_dashboard_stats,
    get_user_activity,
)
from utils.image_processor import enhance_image

load_dotenv()

# ── App Setup ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="MediScript AI",
    description=(
        "Pakistan's First AI Prescription Analyzer\n"
        "HackData V1 | GDGoC CUI Wah\n\n"
        "APIs: OpenFDA FAERS · RxNorm NIH · DailyMed · Google Gemini Vision"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic Models ───────────────────────────────────────────────────────────

class SignupRequest(BaseModel):
    email:     str
    username:  str
    password:  str
    full_name: str = ""


class LoginRequest(BaseModel):
    email:    str
    password: str


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status":    "ok",
        "app":       "MediScript AI",
        "version":   "1.0.0",
        "team":      "Hamza Ali | Muhammad Umair Malik | Shahzaib Shoaib Rathore",
        "hackathon": "HackData V1 | GDGoC CUI Wah",
        "apis": {
            "openfda":  "https://api.fda.gov/drug/event.json",
            "rxnorm":   "https://rxnav.nlm.nih.gov/REST",
            "dailymed": "https://dailymed.nlm.nih.gov/dailymed/services/v2",
            "gemini":   "gemini-1.5-flash (Vision)",
        },
    }


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.post("/auth/signup", tags=["Auth"])
def signup(request: SignupRequest):
    """Register a new user."""
    if not all([request.email, request.password, request.username]):
        raise HTTPException(400, "Email, username, and password are required")
    result = create_user(
        email=request.email,
        username=request.username,
        password=request.password,
        full_name=request.full_name,
    )
    if not result["success"]:
        raise HTTPException(400, result["error"])
    return result


@app.post("/auth/login", tags=["Auth"])
def login(request: LoginRequest):
    """Login a user."""
    result = login_user(email=request.email, password=request.password)
    if not result["success"]:
        raise HTTPException(401, result["error"])
    return result


@app.get("/user/{user_id}", tags=["Auth"])
def get_user(user_id: str):
    """Get user profile by ID."""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user


# ── Main Analysis Endpoint ────────────────────────────────────────────────────

@app.post("/analyze", tags=["Analysis"])
async def analyze_prescription(
    file:    UploadFile = File(...),
    user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    """
    Analyze a prescription image end-to-end.

    Pipeline:
      1. Validate & enhance image
      2. Extract drugs via Gemini Vision (AI)
      3. Safety double-check (AI)
      4. Drug interaction check via OpenFDA + RxNorm (live APIs)
      5. Bilingual explanation — English + Roman Urdu (AI)
      6. Medicine recommendations (AI)
      7. Persist to Supabase
    """
    try:
        # ── Validate file type ────────────────────────────────────────────────
        content_type = (file.content_type or "").lower()
        if content_type and "image" not in content_type and "pdf" not in content_type:
            raise HTTPException(400, "Please upload an image (JPG, PNG, WEBP) or PDF")

        # ── Read & size-check ─────────────────────────────────────────────────
        image_bytes = await file.read()
        if len(image_bytes) > 15_000_000:
            raise HTTPException(400, "File too large — maximum 15 MB")

        # ── 1. Enhance image ──────────────────────────────────────────────────
        enhanced = enhance_image(image_bytes)

        # ── 2. Extract drugs (Gemini Vision) ─────────────────────────────────
        drugs = await extract_drugs(enhanced)

        if not drugs.get("drug_list"):
            return JSONResponse(status_code=200, content={
                "success":  False,
                "error":    "Could not extract drug information from the image.",
                "raw_text": drugs.get("raw_text", ""),
                "tip":      "Try a clearer, well-lit photo of the prescription.",
            })

        # ── 3. Safety double-check (Gemini) ───────────────────────────────────
        double_check = await double_check_prescription(drugs)

        # ── 4. Drug interactions (OpenFDA + RxNorm live APIs) ─────────────────
        interactions = await check_interactions_live(drugs.get("drug_list", []))

        # ── 5. Bilingual explanation (Gemini) ─────────────────────────────────
        explanation = await explain_prescription(drugs, interactions)

        # ── 6. Recommendations (Gemini) ────────────────────────────────────────
        recommendations = await get_recommendations(drugs, interactions)

        # ── 7. Save to Supabase ────────────────────────────────────────────────
        scan_id = save_scan(
            drugs=drugs,
            interactions=interactions,
            explanation=explanation,
            recommendations=recommendations,
            double_check=double_check,
            user_id=user_id,
        )

        return {
            "success":        True,
            "scan_id":        scan_id,
            "drugs":          drugs,
            "double_check":   double_check,
            "interactions":   interactions,
            "explanation":    explanation,
            "recommendations": recommendations,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")


# ── Data Routes ───────────────────────────────────────────────────────────────

@app.get("/history", tags=["Data"])
def get_scan_history(limit: int = 20, user_id: Optional[str] = None):
    """Get recent prescription scans."""
    return get_history(limit=limit, user_id=user_id)


@app.get("/scan/{scan_id}", tags=["Data"])
def get_scan(scan_id: str):
    """Get a specific scan by ID."""
    scan = get_scan_by_id(scan_id)
    if not scan:
        raise HTTPException(404, "Scan not found")
    return scan


@app.get("/analytics", tags=["Data"])
def drug_analytics():
    """Get most-scanned drugs analytics."""
    return get_analytics()


@app.get("/dashboard", tags=["Data"])
def dashboard(user_id: Optional[str] = None):
    """Dashboard stats + top drugs."""
    return {
        "stats":     get_dashboard_stats(user_id=user_id),
        "top_drugs": get_analytics()[:10],
    }


@app.get("/user/{user_id}/activity", tags=["Data"])
def user_activity(user_id: str, limit: int = 20):
    """Get user's recent activity log."""
    return get_user_activity(user_id=user_id, limit=limit)


@app.get("/drug-info/{drug_name}", tags=["Drug Info"])
async def drug_info(drug_name: str):
    """
    Live drug info from OpenFDA label + DailyMed.
    No API key required.
    """
    return await get_drug_info_live(drug_name)


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
