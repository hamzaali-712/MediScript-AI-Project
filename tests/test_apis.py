"""
MediScript AI — Quick API Tests
Run these independently to verify all 3 government APIs are live.

Usage:
    python tests/test_apis.py
"""

import requests
import json


# ── 1. OpenFDA FAERS ─────────────────────────────────────────────────────────

def test_openfda(limit: int = 3):
    """
    Query OpenFDA FAERS adverse event database.
    Endpoint: GET https://api.fda.gov/drug/event.json
    Docs: https://open.fda.gov/apis/drug/event/
    """
    print("\n" + "=" * 55)
    print("TEST 1: OpenFDA FAERS Adverse Event Database")
    print("=" * 55)

    url    = "https://api.fda.gov/drug/event.json"
    params = {"limit": limit}

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", [])
        print(f"✅  Status: {resp.status_code} OK")
        print(f"   Total records in DB: {data.get('meta', {}).get('results', {}).get('total', 'N/A'):,}")
        print(f"   Showing: {len(results)} cases\n")

        for i, item in enumerate(results, 1):
            patient = item.get("patient", {})
            print(f"  CASE {i}")
            for d in patient.get("drug", []):
                print(f"    Drug    : {d.get('medicinalproduct', 'Unknown')}")
            for r in patient.get("reaction", []):
                print(f"    Reaction: {r.get('reactionmeddrapt', 'Unknown')}")
            print()

    except Exception as e:
        print(f"❌  OpenFDA test failed: {e}")


# ── 2. RxNorm NIH ─────────────────────────────────────────────────────────────

def test_rxnorm(drug_name: str = "aspirin"):
    """
    Resolve a drug name to its RxNorm Concept ID (RXCUI).
    Endpoint: GET https://rxnav.nlm.nih.gov/REST/rxcui.json
    Docs: https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html
    """
    print("\n" + "=" * 55)
    print("TEST 2: RxNorm NIH — Drug Concept ID Lookup")
    print("=" * 55)

    url = "https://rxnav.nlm.nih.gov/REST/rxcui.json"

    for name in [drug_name, "ibuprofen", "metformin"]:
        try:
            resp = requests.get(url, params={"name": name, "allsrc": 0}, timeout=10)
            resp.raise_for_status()
            data     = resp.json()
            id_group = data.get("idGroup", {})
            rx_ids   = id_group.get("rxnormId", [])

            if rx_ids:
                print(f"  ✅  {name:20s} → RxNorm ID: {rx_ids[0]}")
            else:
                print(f"  ⚠️   {name:20s} → Not found in RxNorm")
        except Exception as e:
            print(f"  ❌  {name}: Error — {e}")


# ── 3. DailyMed NIH ──────────────────────────────────────────────────────────

def test_dailymed(limit: int = 5):
    """
    Fetch official FDA drug label metadata from DailyMed.
    Endpoint: GET https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json
    Docs: https://dailymed.nlm.nih.gov/dailymed/app-support-web-services.cfm
    """
    print("\n" + "=" * 55)
    print("TEST 3: DailyMed NIH — Official FDA Drug Labels")
    print("=" * 55)

    url = "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json"

    try:
        resp = requests.get(url, params={"limit": limit}, timeout=10)
        resp.raise_for_status()
        data  = resp.json()
        items = data.get("data", [])

        print(f"✅  Status: {resp.status_code} OK")
        print(f"   Showing {len(items)} drug labels:\n")
        for i, item in enumerate(items, 1):
            print(f"  {i:2}. {item.get('title', 'Unknown Title')}")
            print(f"      SetID: {item.get('setid', 'N/A')}")

    except Exception as e:
        print(f"❌  DailyMed test failed: {e}")


# ── Run All Tests ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🔬 MediScript AI — Government API Live Tests")
    print("   All APIs are free, no authentication required.\n")

    test_openfda(limit=3)
    test_rxnorm("aspirin")
    test_dailymed(limit=5)

    print("\n" + "=" * 55)
    print("All tests complete. If you see ✅ for all three,")
    print("your live API connections are working correctly.")
    print("=" * 55 + "\n")
