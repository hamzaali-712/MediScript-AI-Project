"""
MediScript AI — Supabase Database Client
Handles all database operations:
  - User auth (signup / login)
  - Save / retrieve scans
  - Drug analytics
  - User activity log
"""

import os
import json
import hashlib
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

_SUPABASE_URL = os.getenv("SUPABASE_URL", "")
_SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Lazy-initialised client
_client = None


def _get_client():
    """Return a Supabase client, initialising on first call."""
    global _client
    if _client is None:
        if not _SUPABASE_URL or not _SUPABASE_KEY:
            print("[DB] WARNING: SUPABASE_URL / SUPABASE_KEY not set — DB features disabled.")
            return None
        from supabase import create_client
        _client = create_client(_SUPABASE_URL, _SUPABASE_KEY)
    return _client


def _hash_password(password: str) -> str:
    """SHA-256 hash. Use bcrypt in production."""
    return hashlib.sha256(password.encode()).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── User Auth ─────────────────────────────────────────────────────────────────

def create_user(email: str, username: str, password: str, full_name: str = "") -> dict:
    """Register a new user. Returns {success, user} or {success, error}."""
    db = _get_client()
    if not db:
        return {"success": False, "error": "Database not configured"}
    try:
        # Duplicate checks
        if db.table("users").select("id").eq("email", email).execute().data:
            return {"success": False, "error": "Email already registered"}
        if db.table("users").select("id").eq("username", username).execute().data:
            return {"success": False, "error": "Username already taken"}

        result = db.table("users").insert({
            "email":         email,
            "username":      username,
            "password_hash": _hash_password(password),
            "full_name":     full_name,
            "created_at":    _now(),
        }).execute()

        if result.data:
            user = result.data[0]
            _log_activity(user["id"], "signup", {"email": email})
            return {"success": True, "user": _safe_user(user)}
        return {"success": False, "error": "Could not create user"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def login_user(email: str, password: str) -> dict:
    """Authenticate a user. Returns {success, user} or {success, error}."""
    db = _get_client()
    if not db:
        return {"success": False, "error": "Database not configured"}
    try:
        result = (
            db.table("users")
            .select("*")
            .eq("email", email)
            .eq("password_hash", _hash_password(password))
            .execute()
        )
        if result.data:
            user = result.data[0]
            db.table("users").update({"last_login": _now()}).eq("id", user["id"]).execute()
            _log_activity(user["id"], "login", {"email": email})
            return {"success": True, "user": _safe_user(user)}
        return {"success": False, "error": "Invalid email or password"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_user_by_id(user_id: str) -> dict:
    db = _get_client()
    if not db:
        return {}
    try:
        result = (
            db.table("users")
            .select("id,email,username,full_name,created_at,last_login")
            .eq("id", user_id)
            .execute()
        )
        return result.data[0] if result.data else {}
    except Exception:
        return {}


def _safe_user(user: dict) -> dict:
    """Strip sensitive fields before returning to client."""
    return {
        "id":        user.get("id"),
        "email":     user.get("email"),
        "username":  user.get("username"),
        "full_name": user.get("full_name", ""),
    }


# ── Scans ─────────────────────────────────────────────────────────────────────

def save_scan(
    drugs: dict,
    interactions: list,
    explanation: dict,
    recommendations: dict = None,
    double_check: dict = None,
    user_id: str = None,
) -> str:
    """Persist a prescription scan. Returns the new scan ID (or '' on failure)."""
    db = _get_client()
    if not db:
        print("[DB] Supabase not configured — skipping save")
        return ""
    try:
        drug_list = drugs.get("drug_list", [])
        row = {
            "drug_list":        json.dumps(drug_list),
            "interactions":     json.dumps(interactions),
            "explanation_en":   explanation.get("english", ""),
            "explanation_ur":   explanation.get("urdu", ""),
            "warnings":         json.dumps(explanation.get("warnings", [])),
            "tips":             json.dumps(explanation.get("tips", [])),
            "summary":          explanation.get("summary", ""),
            "recommendations":  json.dumps(recommendations or {}),
            "double_check":     json.dumps(double_check or {}),
            "drug_count":       len(drug_list),
            "has_interaction":  len(interactions) > 0,
            "created_at":       _now(),
        }
        if user_id:
            row["user_id"] = user_id

        result  = db.table("scans").insert(row).execute()
        scan_id = result.data[0]["id"] if result.data else ""

        # Update drug analytics counters
        for drug in drug_list:
            name = drug.get("name", "").strip()
            if not name:
                continue
            try:
                ex = db.table("drug_analytics").select("id,scan_count").eq("drug_name", name).execute()
                if ex.data:
                    db.table("drug_analytics").update({
                        "scan_count": ex.data[0]["scan_count"] + 1,
                        "updated_at": _now(),
                    }).eq("drug_name", name).execute()
                else:
                    db.table("drug_analytics").insert({
                        "drug_name":  name,
                        "scan_count": 1,
                        "created_at": _now(),
                    }).execute()
            except Exception:
                pass

        if user_id and scan_id:
            _log_activity(user_id, "scan", {"drug_count": len(drug_list), "scan_id": scan_id})

        return scan_id
    except Exception as e:
        print(f"[DB] Save scan error: {e}")
        return ""


def get_history(limit: int = 20, user_id: str = None) -> list:
    db = _get_client()
    if not db:
        return []
    try:
        q = db.table("scans").select("*").order("created_at", desc=True).limit(limit)
        if user_id:
            q = q.eq("user_id", user_id)
        return q.execute().data or []
    except Exception as e:
        print(f"[DB] History error: {e}")
        return []


def get_scan_by_id(scan_id: str) -> dict:
    db = _get_client()
    if not db:
        return {}
    try:
        result = db.table("scans").select("*").eq("id", scan_id).execute()
        return result.data[0] if result.data else {}
    except Exception:
        return {}


def get_analytics() -> list:
    db = _get_client()
    if not db:
        return []
    try:
        return (
            db.table("drug_analytics")
            .select("*")
            .order("scan_count", desc=True)
            .limit(20)
            .execute()
            .data or []
        )
    except Exception as e:
        print(f"[DB] Analytics error: {e}")
        return []


def get_dashboard_stats(user_id: str = None) -> dict:
    scans = get_history(limit=1000, user_id=user_id)
    return {
        "total_scans":        len(scans),
        "total_interactions": sum(1 for s in scans if s.get("has_interaction")),
        "total_drugs":        sum(s.get("drug_count", 0) for s in scans),
    }


# ── Activity Log ──────────────────────────────────────────────────────────────

def _log_activity(user_id: str, action: str, details: dict = None) -> None:
    db = _get_client()
    if not db:
        return
    try:
        db.table("user_activity").insert({
            "user_id":    user_id,
            "action":     action,
            "details":    json.dumps(details or {}),
            "created_at": _now(),
        }).execute()
    except Exception:
        pass


def get_user_activity(user_id: str, limit: int = 20) -> list:
    db = _get_client()
    if not db:
        return []
    try:
        return (
            db.table("user_activity")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
            .data or []
        )
    except Exception:
        return []
