"""
MediScript AI — Backend Package

Contains:
- FastAPI app (main)
- Gemini AI service
- Drug interaction checker
- Supabase database client
"""

__version__ = "1.0.0"

# Optional: expose key functions for cleaner imports
from .gemini_service import (
    extract_drugs,
    explain_prescription,
    get_recommendations,
    double_check_prescription,
)

from .drug_checker import (
    check_interactions_live,
    get_drug_info_live,
)

from .supabase_client import (
    create_user,
    login_user,
    get_user_by_id,
    save_scan,
)