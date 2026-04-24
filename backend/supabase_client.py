"""
MediScript AI — Supabase Database Client
Handles all database operations:
  - User auth (signup/login)
  - Save/get scans
  - Analytics
  - Activity log
"""

import os
import json
import hashlib
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# ── Initialize Supabase client ────────────────────────────────────────────────
_url = os.getenv("SUPABASE_URL", "")
_key = os.getenv("SUPABASE_KEY", "")

supabase: Client = None

def _get_client() -> Client:
    global supabase
    if supabase is None and _url and _key:
        supabase = create_client(_url, _key)
    return supabase


def _hash_password(password: str) -> str:
    """Simple password hashing (use bcrypt in production)."""
    return hashlib.sha256(password.encode()).hexdigest()


# ── User Auth ─────────────────────────────────────────────────────────────────

def create_user(email: str, username: str, password: str, full_name: str = "") -> dict:
    """Register a new user."""
    db = _get_client()
    if not db:
        return {"success": False, "error": "Database not configured"}
    try:
        # Check if user exists
        existing = db.table("users").select("id").eq("email", email).execute()
        if existing.data:
            return {"success": False, "error": "Email already registered"}
        existing_user = db.table("users").select("id").eq("username", username).execute()
        if existing_user.data:
            return {"success": False, "error": "Username already taken"}

        result = db.table("users").insert({
            "email": email,
            "username": username,
            "password_hash": _hash_password(password),
            "full_name": full_name,
        }).execute()

        if result.data:
            user = result.data[0]
            _log_activity(user["id"], "signup", {"email": email})
            return {"success": True, "user": {
                "id": user["id"],
                "email": user["email"],
                "username": user["username"],
                "full_name": user.get("full_name", ""),
            }}
        return {"success": False, "error": "Could not create user"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def login_user(email: str, password: str) -> dict:
    """Authenticate a user."""
    db = _get_client()
    if not db:
        return {"success": False, "error": "Database not configured"}
    try:
        result = db.table("users").select("*").eq("email", email).eq(
            "password_hash", _hash_password(password)
        ).execute()

        if result.data:
            user = result.data[0]
            # Update last_login
            db.table("users").update({"last_login": datetime.utcnow().isoformat()}).eq(
                "id", user["id"]
            ).execute()
            _log_activity(user["id"], "login", {"email": email})
            return {"success": True, "user": {
                "id": user["id"],
                "email": user["email"],
                "username": user["username"],
                "full_name": user.get("full_name", ""),
            }}
        return {"success": False, "error": "Invalid email or password"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_user_by_id(user_id: str) -> dict:
    """Get user details by ID."""
    db = _get_client()
    if not db:
        return {}
    try:
        result = db.table("users").select("id,email,username,full_name,created_at,last_login").eq(
            "id", user_id
        ).execute()
        return result.data[0] if result.data else {}
    except Exception:
        return {}


# ── Scans ─────────────────────────────────────────────────────────────────────

def save_scan(
    drugs: dict,
    interactions: list,
    explanation: dict,
    recommendations: dict = None,
    double_check: dict = None,
    user_id: str = None,
) -> str:
    """Save a prescription scan to the database. Returns scan ID."""
    db = _get_client()
    if not db:
        print("[DB] Supabase not configured — skipping save")
        return ""
    try:
        drug_list = drugs.get("drug_list", [])
        row = {
            "drug_list": json.dumps(drug_list),
            "interactions": json.dumps(interactions),
            "explanation_en": explanation.get("english", ""),
            "explanation_ur": explanation.get("urdu", ""),
            "warnings": json.dumps(explanation.get("warnings", [])),
            "tips": json.dumps(explanation.get("tips", [])),
            "summary": explanation.get("summary", ""),
            "recommendations": json.dumps(recommendations or {}),
            "double_check": json.dumps(double_check or {}),
            "drug_count": len(drug_list),
            "has_interaction": len(interactions) > 0,
        }
        if user_id:
            row["user_id"] = user_id

        result = db.table("scans").insert(row).execute()
        scan_id = result.data[0]["id"] if result.data else ""

        # Update drug analytics
        for drug in drug_list:
            name = drug.get("name", "").strip()
            if not name:
                continue
            try:
                ex = db.table("drug_analytics").select("id,scan_count").eq(
                    "drug_name", name
                ).execute()
                if ex.data:
                    db.table("drug_analytics").update({
                        "scan_count": ex.data[0]["scan_count"] + 1,
                        "updated_at": datetime.utcnow().isoformat(),
                    }).eq("drug_name", name).execute()
                else:
                    db.table("drug_analytics").insert({
                        "drug_name": name, "scan_count": 1
                    }).execute()
            except Exception:
                pass

        if user_id:
            _log_activity(user_id, "scan", {"drug_count": len(drug_list), "scan_id": scan_id})

        return scan_id
    except Exception as e:
        print(f"[DB] Save scan error: {e}")
        return ""


def get_history(limit: int = 20, user_id: str = None) -> list:
    """Get recent prescription scans."""
    db = _get_client()
    if not db:
        return []
    try:
        query = db.table("scans").select("*").order("created_at", desc=True).limit(limit)
        if user_id:
            query = db.table("scans").select("*").eq("user_id", user_id).order(
                "created_at", desc=True
            ).limit(limit)
        return query.execute().data or []
    except Exception as e:
        print(f"[DB] History error: {e}")
        return []


def get_scan_by_id(scan_id: str) -> dict:
    """Get a specific scan by ID."""
    db = _get_client()
    if not db:
        return {}
    try:
        result = db.table("scans").select("*").eq("id", scan_id).execute()
        return result.data[0] if result.data else {}
    except Exception:
        return {}


def get_analytics() -> list:
    """Get drug analytics (most scanned drugs)."""
    db = _get_client()
    if not db:
        return []
    try:
        return db.table("drug_analytics").select("*").order(
            "scan_count", desc=True
        ).limit(20).execute().data or []
    except Exception as e:
        print(f"[DB] Analytics error: {e}")
        return []


def get_dashboard_stats(user_id: str = None) -> dict:
    """Get summary stats for the dashboard."""
    db = _get_client()
    if not db:
        return {"total_scans": 0, "total_interactions": 0, "total_drugs": 0}
    try:
        scans = get_history(limit=1000, user_id=user_id)
        total_scans = len(scans)
        total_interactions = sum(1 for s in scans if s.get("has_interaction"))
        total_drugs = sum(s.get("drug_count", 0) for s in scans)
        return {
            "total_scans": total_scans,
            "total_interactions": total_interactions,
            "total_drugs": total_drugs,
        }
    except Exception:
        return {"total_scans": 0, "total_interactions": 0, "total_drugs": 0}


# ── Activity Log ──────────────────────────────────────────────────────────────

def _log_activity(user_id: str, action: str, details: dict = None) -> None:
    """Log user activity."""
    db = _get_client()
    if not db:
        return
    try:
        db.table("user_activity").insert({
            "user_id": user_id,
            "action": action,
            "details": json.dumps(details or {}),
        }).execute()
    except Exception:
        pass


def get_user_activity(user_id: str, limit: int = 20) -> list:
    """Get user's recent activity."""
    db = _get_client()
    if not db:
        return []
    try:
        return db.table("user_activity").select("*").eq("user_id", user_id).order(
            "created_at", desc=True
        ).limit(limit).execute().data or []
    except Exception:
        return []
