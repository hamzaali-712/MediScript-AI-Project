"""
MediScript AI — FastAPI Backend Server
HackData V1 | GDGoC CUI Wah
Team: Hamza Ali (Project Idea) | Muhammad Umair Malik | Shahzaib Shoaib Rathore

Routes:
  GET  /health          - Health check
  POST /auth/signup     - Register new user
  POST /auth/login      - Login user
  POST /analyze         - Analyze prescription (main endpoint)
  GET  /history         - Get scan history
  GET  /scan/{id}       - Get specific scan
  GET  /analytics       - Drug analytics
  GET  /dashboard       - Dashboard stats
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
    description="Pakistan's First AI Prescription Analyzer | HackData V1 | GDGoC CUI Wah",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic Models ───────────────────────────────────────────────────────────
class SignupRequest(BaseModel):
    email: str
    username: str
    password: str
    full_name: str = ""


class LoginRequest(BaseModel):
    email: str
    password: str


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": "MediScript AI",
        "version": "1.0.0",
        "team": "Hamza Ali | Muhammad Umair Malik | Shahzaib Shoaib Rathore",
        "hackathon": "HackData V1 | GDGoC CUI Wah",
    }


# ── Auth Routes ───────────────────────────────────────────────────────────────

@app.post("/auth/signup")
def signup(request: SignupRequest):
    """Register a new user."""
    if not request.email or not request.password or not request.username:
        raise HTTPException(status_code=400, detail="Email, username, and password required")
    result = create_user(
        email=request.email,
        username=request.username,
        password=request.password,
        full_name=request.full_name,
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post("/auth/login")
def login(request: LoginRequest):
    """Login a user."""
    result = login_user(email=request.email, password=request.password)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])
    return result


@app.get("/user/{user_id}")
def get_user(user_id: str):
    """Get user profile."""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ── Main Analysis Route ───────────────────────────────────────────────────────

@app.post("/analyze")
async def analyze_prescription(
    file: UploadFile = File(...),
    user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    """
    Main endpoint: analyze a prescription image.
    Steps:
      1. Enhance image quality
      2. Extract drugs via Gemini Vision (Anti-Gravity)
      3. Double-check extraction accuracy
      4. Check drug interactions via live FDA/NIH APIs
      5. Generate bilingual explanation (English + Roman Urdu)
      6. Generate medicine recommendations
      7. Save to Supabase
    """
    try:
        # Validate file type
        if file.content_type and "image" not in file.content_type.lower():
            if "pdf" not in file.content_type.lower():
                raise HTTPException(
                    status_code=400, detail="Please upload an image file (JPG, PNG, WEBP)"
                )

        # Read and enhance image
        image_bytes = await file.read()
        if len(image_bytes) > 15_000_000:
            raise HTTPException(status_code=400, detail="File too large. Maximum 15MB.")
        enhanced_bytes = enhance_image(image_bytes)

        # Step 1: Extract drugs via Gemini Vision
        drugs = await extract_drugs(enhanced_bytes)

        if not drugs.get("drug_list"):
            # Return partial result with raw text for debugging
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "error": "Could not extract drug information from the image.",
                    "raw_text": drugs.get("raw_text", ""),
                    "tip": "Try a clearer, well-lit photo of the prescription.",
                },
            )

        # Step 2: Double-check extraction
        double_check = await double_check_prescription(drugs)

        # Step 3: Check drug interactions via live APIs
        interactions = await check_interactions_live(drugs.get("drug_list", []))

        # Step 4: Generate bilingual explanation
        explanation = await explain_prescription(drugs, interactions)

        # Step 5: Get medicine recommendations
        recommendations = await get_recommendations(drugs, interactions)

        # Step 6: Save to database
        scan_id = save_scan(
            drugs=drugs,
            interactions=interactions,
            explanation=explanation,
            recommendations=recommendations,
            double_check=double_check,
            user_id=user_id,
        )

        return {
            "success": True,
            "scan_id": scan_id,
            "drugs": drugs,
            "double_check": double_check,
            "interactions": interactions,
            "explanation": explanation,
            "recommendations": recommendations,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ── Data Routes ───────────────────────────────────────────────────────────────

@app.get("/history")
def get_scan_history(
    limit: int = 20,
    user_id: Optional[str] = None,
):
    """Get recent scan history."""
    return get_history(limit=limit, user_id=user_id)


@app.get("/scan/{scan_id}")
def get_scan(scan_id: str):
    """Get a specific scan by ID."""
    scan = get_scan_by_id(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


@app.get("/analytics")
def get_drug_analytics():
    """Get drug analytics data."""
    return get_analytics()


@app.get("/dashboard")
def get_dashboard(user_id: Optional[str] = None):
    """Get dashboard statistics."""
    stats = get_dashboard_stats(user_id=user_id)
    analytics = get_analytics()
    return {"stats": stats, "top_drugs": analytics[:10]}


@app.get("/user/{user_id}/activity")
def get_activity(user_id: str, limit: int = 20):
    """Get user activity log."""
    return get_user_activity(user_id=user_id, limit=limit)


@app.get("/drug-info/{drug_name}")
async def drug_info(drug_name: str):
    """Get drug info from live APIs."""
    return await get_drug_info_live(drug_name)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
