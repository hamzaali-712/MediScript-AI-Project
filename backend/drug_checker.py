"""
MediScript AI — Drug Interaction Checker
Uses LIVE government APIs (no CSV downloads needed, zero cost):
  - OpenFDA FAERS API (500K+ adverse event reports)
  - RxNorm NIH API (unlimited, no key)
  - DailyMed API (official FDA drug labels)
"""

import requests
import asyncio
import os
from fuzzywuzzy import fuzz

OPENFDA_BASE = "https://api.fda.gov/drug"
RXNORM_BASE = "https://rxnav.nlm.nih.gov/REST"
DAILYMED_BASE = "https://dailymed.nlm.nih.gov/dailymed/services/v2"

REQUEST_TIMEOUT = 8  # seconds


# ── OpenFDA Live API ─────────────────────────────────────────────────────────

def _check_openfda_interaction(drug1: str, drug2: str) -> dict:
    """Call OpenFDA FAERS database directly. No key needed. 500K+ records."""
    try:
        url = f"{OPENFDA_BASE}/druginteractions.json"
        params = {
            "search": f'patient.drug.medicinalproduct:"{drug1}"',
            "limit": 50,
        }
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            return {}

        for event in resp.json().get("results", []):
            drug_names = [
                d.get("medicinalproduct", "").lower()
                for d in event.get("patient", {}).get("drug", [])
            ]
            # Fuzzy match drug2
            if any(fuzz.partial_ratio(drug2.lower(), n) > 75 for n in drug_names):
                serious = event.get("serious", 0)
                reactions = event.get("patient", {}).get("reaction", [])
                desc = reactions[0].get("reactionmeddrapt", "") if reactions else ""
                return {
                    "drug1": drug1,
                    "drug2": drug2,
                    "severity": "SEVERE" if serious == 1 else "MODERATE",
                    "description": (
                        f"{drug1} and {drug2} have been reported together in "
                        f"FDA adverse events database. "
                        + (f"Reaction: {desc}." if desc else "")
                    ).strip(),
                    "source": "OpenFDA FAERS (500K+ reports)",
                }
    except requests.Timeout:
        pass
    except Exception as e:
        print(f"[OpenFDA] Error checking {drug1}+{drug2}: {e}")
    return {}


def _get_openfda_label_info(drug_name: str) -> dict:
    """Get drug label info (purpose, warnings) from OpenFDA label API."""
    try:
        url = f"{OPENFDA_BASE}/label.json"
        params = {"search": f'openfda.brand_name:"{drug_name}"', "limit": 1}
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            if results:
                label = results[0]
                purpose = label.get("purpose", [""])[0][:200] if label.get("purpose") else ""
                warnings = label.get("warnings", [""])[0][:300] if label.get("warnings") else ""
                dosage = (
                    label.get("dosage_and_administration", [""])[0][:200]
                    if label.get("dosage_and_administration")
                    else ""
                )
                return {"purpose": purpose, "warnings": warnings, "dosage": dosage}
    except Exception as e:
        print(f"[OpenFDA Label] Error for {drug_name}: {e}")
    return {}


# ── RxNorm NIH API ───────────────────────────────────────────────────────────

def _get_rxcui(drug_name: str) -> str:
    """Get RxNorm concept ID for a drug name."""
    try:
        resp = requests.get(
            f"{RXNORM_BASE}/drugs.json",
            params={"name": drug_name},
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            return ""
        groups = resp.json().get("drugGroup", {}).get("conceptGroup", [])
        for group in groups:
            concepts = group.get("conceptProperties", [])
            if concepts:
                return concepts[0].get("rxcui", "")
    except Exception as e:
        print(f"[RxNorm] Error getting RXCUI for {drug_name}: {e}")
    return ""


def _check_rxnorm_interaction(drug1: str, drug2: str) -> dict:
    """Check RxNorm NIH database for drug interactions. Unlimited, no key."""
    try:
        rxcui1 = _get_rxcui(drug1)
        if not rxcui1:
            return {}

        resp = requests.get(
            f"{RXNORM_BASE}/interaction/interaction.json",
            params={"rxcui": rxcui1},
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            return {}

        for grp in resp.json().get("interactionTypeGroup", []):
            for t in grp.get("interactionType", []):
                for pair in t.get("interactionPair", []):
                    desc = pair.get("description", "")
                    if fuzz.partial_ratio(drug2.lower(), desc.lower()) > 65:
                        severity_raw = pair.get("severity", "moderate").upper()
                        severity_map = {
                            "HIGH": "SEVERE",
                            "MEDIUM": "MODERATE",
                            "LOW": "MILD",
                        }
                        severity = severity_map.get(severity_raw, "MODERATE")
                        return {
                            "drug1": drug1,
                            "drug2": drug2,
                            "severity": severity,
                            "description": desc,
                            "source": "NLM RxNorm Database",
                        }
    except Exception as e:
        print(f"[RxNorm] Error checking {drug1}+{drug2}: {e}")
    return {}


# ── DailyMed API ─────────────────────────────────────────────────────────────

def _get_dailymed_info(drug_name: str) -> dict:
    """Get official drug label data from DailyMed (NIH). No key needed."""
    try:
        resp = requests.get(
            f"{DAILYMED_BASE}/drugnames.json",
            params={"drug_name": drug_name},
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code == 200:
            data = resp.json()
            drugs = data.get("data", [])
            if drugs:
                return {"dailymed_name": drugs[0].get("drug_name", drug_name)}
    except Exception as e:
        print(f"[DailyMed] Error for {drug_name}: {e}")
    return {}


# ── Main Interaction Checker ─────────────────────────────────────────────────

async def check_interactions_live(drug_list: list) -> list:
    """
    Check all drug pairs using live government APIs.
    Tries OpenFDA first, falls back to RxNorm.
    """
    results = []
    names = [d.get("name", "").strip() for d in drug_list if d.get("name", "").strip()]

    if len(names) < 2:
        return results

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            d1, d2 = names[i], names[j]

            # Try OpenFDA first
            interaction = await asyncio.get_event_loop().run_in_executor(
                None, _check_openfda_interaction, d1, d2
            )

            # Fallback to RxNorm
            if not interaction:
                interaction = await asyncio.get_event_loop().run_in_executor(
                    None, _check_rxnorm_interaction, d1, d2
                )

            if interaction:
                results.append(interaction)

    # Sort: SEVERE first
    severity_order = {"SEVERE": 0, "MODERATE": 1, "MILD": 2}
    results.sort(key=lambda x: severity_order.get(x.get("severity", "MILD"), 2))
    return results


async def get_drug_info_live(drug_name: str) -> dict:
    """Get comprehensive drug info from live APIs."""
    label_info = await asyncio.get_event_loop().run_in_executor(
        None, _get_openfda_label_info, drug_name
    )
    dailymed_info = await asyncio.get_event_loop().run_in_executor(
        None, _get_dailymed_info, drug_name
    )
    return {**label_info, **dailymed_info, "drug_name": drug_name}
