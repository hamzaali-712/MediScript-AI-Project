"""
MediScript AI — Drug Interaction Checker
Live government APIs (zero cost, no CSV downloads needed):
  - OpenFDA FAERS API  : 500K+ adverse event reports
  - RxNorm NIH API     : drug concept lookup + interactions (unlimited, no key)
  - DailyMed API       : official FDA drug labels (no key)
"""

import os
import asyncio
import requests
from fuzzywuzzy import fuzz
from dotenv import load_dotenv

load_dotenv()

# ── Constants ─────────────────────────────────────────────────────────────────

OPENFDA_BASE   = "https://api.fda.gov/drug"
RXNORM_BASE    = "https://rxnav.nlm.nih.gov/REST"
DAILYMED_BASE  = "https://dailymed.nlm.nih.gov/dailymed/services/v2"
REQUEST_TIMEOUT = 10  # seconds

# Optional FDA key removes rate limits
_OPENFDA_KEY = os.getenv("OPENFDA_API_KEY", "")


def _fda_params(extra: dict) -> dict:
    """Add optional FDA API key to params dict."""
    if _OPENFDA_KEY:
        extra["api_key"] = _OPENFDA_KEY
    return extra


# ── OpenFDA: Adverse Event Reports ───────────────────────────────────────────

def _check_openfda_interaction(drug1: str, drug2: str) -> dict:
    """
    Query OpenFDA FAERS database for co-reported adverse events.
    Endpoint: GET /drug/event.json
    Docs: https://open.fda.gov/apis/drug/event/
    """
    try:
        url    = f"{OPENFDA_BASE}/event.json"
        params = _fda_params({
            "search": f'patient.drug.medicinalproduct:"{drug1}"',
            "limit": 50,
        })
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)

        if resp.status_code == 404:
            return {}  # No records — not an error
        resp.raise_for_status()

        for event in resp.json().get("results", []):
            drug_names = [
                d.get("medicinalproduct", "").lower()
                for d in event.get("patient", {}).get("drug", [])
            ]
            # Fuzzy-match drug2 against co-reported drugs
            if any(fuzz.partial_ratio(drug2.lower(), n) > 75 for n in drug_names):
                serious   = event.get("serious", 0)
                reactions = event.get("patient", {}).get("reaction", [])
                reaction  = reactions[0].get("reactionmeddrapt", "") if reactions else ""
                return {
                    "drug1":       drug1,
                    "drug2":       drug2,
                    "severity":    "SEVERE" if serious == 1 else "MODERATE",
                    "description": (
                        f"{drug1} and {drug2} co-reported in FDA adverse events database."
                        + (f" Reaction: {reaction}." if reaction else "")
                    ).strip(),
                    "source": "OpenFDA FAERS (500K+ reports)",
                }
    except requests.HTTPError as e:
        print(f"[OpenFDA] HTTP {e.response.status_code} for {drug1}+{drug2}")
    except requests.Timeout:
        print(f"[OpenFDA] Timeout for {drug1}+{drug2}")
    except Exception as e:
        print(f"[OpenFDA] Unexpected error for {drug1}+{drug2}: {e}")
    return {}


def _get_openfda_label_info(drug_name: str) -> dict:
    """
    Fetch brand-name drug label (purpose, warnings, dosage).
    Endpoint: GET /drug/label.json
    Docs: https://open.fda.gov/apis/drug/label/
    """
    try:
        url    = f"{OPENFDA_BASE}/label.json"
        params = _fda_params({
            "search": f'openfda.brand_name:"{drug_name}"',
            "limit": 1,
        })
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 404:
            return {}
        resp.raise_for_status()

        results = resp.json().get("results", [])
        if not results:
            return {}

        label   = results[0]
        purpose  = (label.get("purpose")  or [""])[0][:200]
        warnings = (label.get("warnings") or [""])[0][:300]
        dosage   = (label.get("dosage_and_administration") or [""])[0][:200]
        return {"purpose": purpose, "warnings": warnings, "dosage": dosage}

    except Exception as e:
        print(f"[OpenFDA Label] Error for {drug_name}: {e}")
    return {}


# ── RxNorm NIH: Drug Concept + Interaction Lookup ────────────────────────────

def _get_rxcui(drug_name: str) -> str:
    """
    Resolve drug name → RxNorm Concept Unique Identifier (RXCUI).
    Endpoint: GET /rxcui.json
    Docs: https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html
    """
    try:
        resp = requests.get(
            f"{RXNORM_BASE}/rxcui.json",
            params={"name": drug_name, "allsrc": 0},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        id_group = resp.json().get("idGroup", {})
        rx_ids   = id_group.get("rxnormId", [])
        return rx_ids[0] if rx_ids else ""
    except Exception as e:
        print(f"[RxNorm] RXCUI lookup failed for {drug_name}: {e}")
    return ""


def _check_rxnorm_interaction(drug1: str, drug2: str) -> dict:
    """
    Check NLM RxNorm interaction database by RXCUI.
    Endpoint: GET /interaction/interaction.json
    Docs: https://lhncbc.nlm.nih.gov/RxNav/APIs/InteractionAPIs.html
    """
    try:
        rxcui1 = _get_rxcui(drug1)
        if not rxcui1:
            return {}

        resp = requests.get(
            f"{RXNORM_BASE}/interaction/interaction.json",
            params={"rxcui": rxcui1, "sources": "DrugBank"},
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code == 404:
            return {}
        resp.raise_for_status()

        severity_map = {"high": "SEVERE", "medium": "MODERATE", "low": "MILD"}

        for grp in resp.json().get("interactionTypeGroup", []):
            for t in grp.get("interactionType", []):
                for pair in t.get("interactionPair", []):
                    desc = pair.get("description", "")
                    if fuzz.partial_ratio(drug2.lower(), desc.lower()) > 65:
                        raw_sev  = pair.get("severity", "medium").lower()
                        severity = severity_map.get(raw_sev, "MODERATE")
                        return {
                            "drug1":       drug1,
                            "drug2":       drug2,
                            "severity":    severity,
                            "description": desc,
                            "source":      "NLM RxNorm / DrugBank",
                        }
    except Exception as e:
        print(f"[RxNorm Interaction] Error for {drug1}+{drug2}: {e}")
    return {}


# ── DailyMed NIH: Official FDA Drug Labels ───────────────────────────────────

def _get_dailymed_info(drug_name: str) -> dict:
    """
    Fetch official drug label metadata from DailyMed (NIH).
    Endpoint: GET /spls.json
    Docs: https://dailymed.nlm.nih.gov/dailymed/app-support-web-services.cfm
    """
    try:
        resp = requests.get(
            f"{DAILYMED_BASE}/spls.json",
            params={"drug_name": drug_name, "limit": 1},
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code == 404:
            return {}
        resp.raise_for_status()

        items = resp.json().get("data", [])
        if items:
            return {
                "dailymed_name":  items[0].get("title", drug_name),
                "dailymed_setid": items[0].get("setid", ""),
            }
    except Exception as e:
        print(f"[DailyMed] Error for {drug_name}: {e}")
    return {}


# ── Public Async API ──────────────────────────────────────────────────────────

async def check_interactions_live(drug_list: list) -> list:
    """
    Check all drug pairs using live government APIs.
    Strategy: try OpenFDA FAERS first → fallback to RxNorm NIH.
    Returns list of interactions sorted by severity (SEVERE first).
    """
    results = []
    names = [
        d.get("name", "").strip()
        for d in drug_list
        if d.get("name", "").strip()
    ]

    if len(names) < 2:
        return results

    loop = asyncio.get_event_loop()

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            d1, d2 = names[i], names[j]

            # OpenFDA first
            interaction = await loop.run_in_executor(
                None, _check_openfda_interaction, d1, d2
            )

            # Fallback to RxNorm
            if not interaction:
                interaction = await loop.run_in_executor(
                    None, _check_rxnorm_interaction, d1, d2
                )

            if interaction:
                results.append(interaction)

    # Sort: SEVERE → MODERATE → MILD
    order = {"SEVERE": 0, "MODERATE": 1, "MILD": 2}
    results.sort(key=lambda x: order.get(x.get("severity", "MILD"), 2))
    return results


async def get_drug_info_live(drug_name: str) -> dict:
    """
    Aggregate drug info from OpenFDA label + DailyMed.
    Returns combined dict with purpose, warnings, dosage, dailymed metadata.
    """
    loop = asyncio.get_event_loop()
    label_info, dailymed_info = await asyncio.gather(
        loop.run_in_executor(None, _get_openfda_label_info, drug_name),
        loop.run_in_executor(None, _get_dailymed_info, drug_name),
    )
    return {"drug_name": drug_name, **label_info, **dailymed_info}
