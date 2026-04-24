"""
MediScript AI — Gemini Service (Anti-Gravity API)
Handles all Google Gemini AI calls:
  - Drug extraction from prescription images
  - Bilingual explanation (English + Roman Urdu)
  - Medicine recommendations
  - Double-check / verification
"""

import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

# ── Configure Gemini (Anti-Gravity) ──────────────────────────────────────────
genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
model = genai.GenerativeModel("gemini-1.5-flash")


# ── JSON helper ───────────────────────────────────────────────────────────────
def _parse_json(text: str) -> dict:
    """Safely extract JSON from Gemini response text."""
    if not text:
        return {}
    # Direct parse
    try:
        return json.loads(text.strip())
    except Exception:
        pass
    # Strip markdown fences
    clean = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    try:
        return json.loads(clean)
    except Exception:
        pass
    # Find first JSON object
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return {}


# ── PROMPT 1: Drug Extraction (Vision) ───────────────────────────────────────
EXTRACT_PROMPT = """
You are an expert medical AI trained to read prescription images accurately.

Analyze this prescription photo and extract ALL visible medications.

RULES:
- Extract every drug even if partially visible or handwritten
- Decode abbreviations: BID=twice/day, TID=3x/day, QID=4x/day, OD=once/day
- PRN=as needed, SOS=if necessary, HS=bedtime, AC=before meals, PC=after meals
- STAT=immediately, PO=oral, TAB=tablet, CAP=capsule
- Identify dosage strength (500mg, 250mcg, 10ml)
- Include duration (5 days, 1 week, 1 month)
- If text is unclear write 'unclear' — NEVER guess wrongly
- Return ONLY valid JSON — no preamble, no markdown, no explanation

OUTPUT FORMAT (return exactly this structure):
{
  "drug_list": [
    {
      "name": "drug name as written on prescription",
      "generic_name": "generic name if known else same as name",
      "dosage": "e.g. 500mg or unclear",
      "frequency": "e.g. BID or unclear",
      "frequency_readable": "e.g. Twice daily",
      "duration": "e.g. 5 days or unclear",
      "route": "oral/topical/IV/unclear",
      "instructions": "any special instructions like take with food"
    }
  ],
  "doctor_name": "if visible else unknown",
  "patient_name": "if visible else unknown",
  "date": "if visible else unknown",
  "diagnosis": "if visible or inferred else unknown",
  "raw_text": "all text you can read from the image"
}

CRITICAL: Return ONLY the JSON object. Nothing else.
"""


# ── PROMPT 2: Bilingual Explanation ──────────────────────────────────────────
EXPLAIN_PROMPT_TEMPLATE = """
You are a friendly, expert pharmacist in Pakistan helping a patient understand their prescription.
The patient may not have medical knowledge. Explain clearly and simply.

Drugs prescribed:
{drugs}

Drug interactions detected:
{interactions}

RULES:
1. English must be simple — no medical jargon
2. Roman Urdu = Urdu language written in English letters (NOT Urdu script)
3. Roman Urdu example: 'Yeh dawai subah aur shaam leni hai. Khane ke baad lijiye.'
4. Warnings must be specific and actionable
5. Tips must be practical and helpful
6. Return ONLY valid JSON — no extra text

OUTPUT FORMAT:
{
  "english": "Clear, simple English explanation. For each drug: what it is, how/when to take it, main side effects. Mention interactions clearly.",
  "urdu": "Sab dawaiyon ki wazahat Roman Urdu mein. Har dawai ke baare mein batayein. Interactions bhi batayein. Example: Aspirin ek dard ki dawai hai. Din mein 2 dafa leni hai khane ke baad.",
  "warnings": ["Specific warning 1", "Specific warning 2"],
  "tips": ["Take with a full glass of water", "Store below 25 degrees Celsius"],
  "summary": "One sentence: what condition this prescription is treating"
}

Return ONLY the JSON.
"""


# ── PROMPT 3: Medicine Recommendations ───────────────────────────────────────
RECOMMEND_PROMPT_TEMPLATE = """
You are a senior clinical pharmacist in Pakistan reviewing a prescription.

Patient's current drugs:
{drugs}

Detected interactions:
{interactions}

Based on the above, provide:
1. Safe alternative suggestions if dangerous interactions exist
2. OTC supplements that support recovery (e.g. probiotics with antibiotics)
3. Lifestyle and dietary recommendations

RULES:
- NEVER recommend removing a doctor-prescribed drug without flagging it gently
- Be Pakistan-context aware (common available generics, local brand names)
- Return ONLY valid JSON

OUTPUT FORMAT:
{
  "alternatives": [
    {"original": "drug_name", "alternative": "safer_option", "reason": "why safer"}
  ],
  "supplements": [
    {"name": "supplement", "purpose": "why recommended", "dose": "how much"}
  ],
  "dietary": ["Avoid grapefruit with this medication", "Drink 8 glasses of water daily"],
  "lifestyle": ["Avoid driving if feeling dizzy", "Do not stop antibiotics early"],
  "urgency": "normal | consult_soon | urgent"
}

Return ONLY the JSON.
"""


# ── PROMPT 4: Double Check / Verification ────────────────────────────────────
DOUBLE_CHECK_PROMPT_TEMPLATE = """
You are a senior medical reviewer and patient safety expert.

Re-verify this extracted prescription data for accuracy and safety:

Extracted drugs:
{drugs}

RULES:
- Check if dosages are within safe standard ranges
- Flag anything that looks like an OCR/AI extraction error
- Check for any missing critical information
- Return ONLY valid JSON

OUTPUT FORMAT:
{
  "verified": true/false,
  "confidence": "high | medium | low",
  "issues": [
    {"drug": "drug_name", "issue": "description of problem", "severity": "critical|warning|info"}
  ],
  "dosage_checks": [
    {"drug": "drug_name", "extracted_dose": "500mg", "typical_range": "250-1000mg", "status": "ok|high|low|unclear"}
  ],
  "extraction_quality": "good | partial | poor",
  "notes": "Any additional notes for the pharmacist"
}

Return ONLY the JSON.
"""


# ── Public API Functions ──────────────────────────────────────────────────────

async def extract_drugs(image_bytes: bytes) -> dict:
    """Send prescription image to Gemini Vision and return structured drug data."""
    try:
        img_part = {"mime_type": "image/jpeg", "data": image_bytes}
        response = model.generate_content([EXTRACT_PROMPT, img_part])
        result = _parse_json(response.text)
        if not result:
            return {
                "drug_list": [],
                "raw_text": response.text,
                "error": "Could not parse Gemini response as JSON",
            }
        return result
    except Exception as e:
        return {"drug_list": [], "raw_text": "", "error": str(e)}


async def explain_prescription(drugs: dict, interactions: list) -> dict:
    """Generate bilingual (English + Roman Urdu) explanation of prescription."""
    try:
        prompt = EXPLAIN_PROMPT_TEMPLATE.format(
            drugs=json.dumps(drugs.get("drug_list", []), indent=2),
            interactions=json.dumps(interactions, indent=2),
        )
        response = model.generate_content(prompt)
        result = _parse_json(response.text)
        if not result:
            return {
                "english": response.text,
                "urdu": "",
                "warnings": [],
                "tips": [],
                "summary": "",
            }
        return result
    except Exception as e:
        return {"english": str(e), "urdu": "", "warnings": [], "tips": [], "summary": ""}


async def get_recommendations(drugs: dict, interactions: list) -> dict:
    """Get AI-powered medicine recommendations and lifestyle advice."""
    try:
        prompt = RECOMMEND_PROMPT_TEMPLATE.format(
            drugs=json.dumps(drugs.get("drug_list", []), indent=2),
            interactions=json.dumps(interactions, indent=2),
        )
        response = model.generate_content(prompt)
        result = _parse_json(response.text)
        if not result:
            return {
                "alternatives": [],
                "supplements": [],
                "dietary": [],
                "lifestyle": [],
                "urgency": "normal",
            }
        return result
    except Exception as e:
        return {
            "alternatives": [],
            "supplements": [],
            "dietary": [],
            "lifestyle": [],
            "urgency": "normal",
            "error": str(e),
        }


async def double_check_prescription(drugs: dict) -> dict:
    """Verify extracted drug data for safety and accuracy."""
    try:
        prompt = DOUBLE_CHECK_PROMPT_TEMPLATE.format(
            drugs=json.dumps(drugs.get("drug_list", []), indent=2)
        )
        response = model.generate_content(prompt)
        result = _parse_json(response.text)
        if not result:
            return {
                "verified": False,
                "confidence": "low",
                "issues": [],
                "dosage_checks": [],
                "extraction_quality": "poor",
                "notes": response.text,
            }
        return result
    except Exception as e:
        return {
            "verified": False,
            "confidence": "low",
            "issues": [],
            "dosage_checks": [],
            "extraction_quality": "poor",
            "notes": str(e),
        }
