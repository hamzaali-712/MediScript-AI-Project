"""
MediScript AI — Gemini Vision Service
Handles all Google Gemini AI calls:
  - Drug extraction from prescription images (Vision)
  - Bilingual explanation (English + Roman Urdu)
  - Medicine recommendations
  - Double-check / safety verification
"""

import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# ── Configure Gemini ──────────────────────────────────────────────────────────

_api_key = os.getenv("GEMINI_API_KEY", "")
if not _api_key:
    print("[Gemini] WARNING: GEMINI_API_KEY not set. AI features will fail.")

genai.configure(api_key=_api_key)
model = genai.GenerativeModel("gemini-1.5-flash")


# ── JSON Parsing Helper ───────────────────────────────────────────────────────

def _parse_json(text: str) -> dict:
    """Robustly extract JSON from Gemini response (handles markdown fences)."""
    if not text:
        return {}
    # 1) Direct parse
    try:
        return json.loads(text.strip())
    except Exception:
        pass
    # 2) Strip markdown code fences
    clean = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    try:
        return json.loads(clean)
    except Exception:
        pass
    # 3) Extract first JSON object
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return {}


# ── Prompts ───────────────────────────────────────────────────────────────────

_EXTRACT_PROMPT = """
You are an expert medical AI trained to read prescription images accurately.

Analyze this prescription image and extract ALL visible medications.

ABBREVIATION DECODER:
  BID/BD = twice daily | TID = 3x daily | QID = 4x daily | OD = once daily
  PRN/SOS = as needed  | HS = bedtime   | AC = before meals | PC = after meals
  STAT = immediately   | PO = oral      | TAB = tablet      | CAP = capsule

RULES:
- Extract EVERY drug, even if partially visible or handwritten
- Identify dosage strength (500mg, 250mcg, 10ml)
- Include duration (5 days, 1 week, 1 month)
- If text is unclear → write "unclear" — NEVER guess wrongly
- Return ONLY valid JSON — no preamble, no markdown, no explanation

OUTPUT FORMAT (return exactly this structure):
{
  "drug_list": [
    {
      "name": "drug name as written",
      "generic_name": "generic name if known, else same as name",
      "dosage": "e.g. 500mg or unclear",
      "frequency": "e.g. BID or unclear",
      "frequency_readable": "e.g. Twice daily",
      "duration": "e.g. 5 days or unclear",
      "route": "oral/topical/IV/unclear",
      "instructions": "e.g. Take with food after meals"
    }
  ],
  "doctor_name": "if visible else unknown",
  "patient_name": "if visible else unknown",
  "date": "if visible else unknown",
  "diagnosis": "if visible or inferable else unknown",
  "raw_text": "all text you can read from the image"
}

CRITICAL: Return ONLY the JSON object. Nothing else.
"""

_EXPLAIN_TEMPLATE = """
You are a friendly, expert pharmacist in Pakistan helping a patient understand their prescription.
The patient may not have medical knowledge — explain clearly and simply.

Drugs prescribed:
{drugs}

Drug interactions detected:
{interactions}

RULES:
1. English must be simple — avoid medical jargon
2. Roman Urdu = Urdu language written in English letters (NOT Urdu script, NOT English)
   Example: "Yeh dawai subah aur shaam leni hai. Khane ke baad lijiye."
3. Warnings must be specific and actionable
4. Tips must be practical and relevant
5. Return ONLY valid JSON — no extra text

OUTPUT FORMAT:
{{
  "english": "Clear English explanation per drug: what it is, when/how to take it, main side effects. Mention interactions explicitly.",
  "urdu": "Sab dawaiyon ki wazahat Roman Urdu mein. Misal: Amoxicillin ek antibiotic hai. Subah, dopahar aur raat ko leni hai. Poora course complete karein.",
  "warnings": ["Warning 1 specific to this prescription", "Warning 2"],
  "tips": ["Take with a full glass of water", "Store below 25 degrees Celsius"],
  "summary": "One sentence describing what condition this prescription treats"
}}

Return ONLY the JSON.
"""

_RECOMMEND_TEMPLATE = """
You are a senior clinical pharmacist in Pakistan reviewing a prescription.

Patient's current drugs:
{drugs}

Detected interactions:
{interactions}

Provide:
1. Safe alternatives if dangerous interactions exist
2. OTC supplements that support recovery (e.g. probiotics with antibiotics)
3. Pakistan-specific dietary and lifestyle advice

RULES:
- NEVER recommend stopping a doctor-prescribed drug — only flag gently
- Use Pakistan-available generics and local brand names where relevant
- Return ONLY valid JSON

OUTPUT FORMAT:
{{
  "alternatives": [
    {{"original": "drug_name", "alternative": "safer_option", "reason": "why safer"}}
  ],
  "supplements": [
    {{"name": "supplement", "purpose": "why recommended", "dose": "suggested amount"}}
  ],
  "dietary": ["Avoid grapefruit with this medication", "Drink 8 glasses of water daily"],
  "lifestyle": ["Avoid driving if feeling dizzy", "Do not stop antibiotics early"],
  "urgency": "normal | consult_soon | urgent"
}}

Return ONLY the JSON.
"""

_DOUBLE_CHECK_TEMPLATE = """
You are a senior medical reviewer and patient safety expert.

Re-verify this extracted prescription for accuracy and safety:

Extracted drugs:
{drugs}

RULES:
- Check if dosages are within standard safe ranges
- Flag anything that looks like an OCR/AI extraction error
- Note any missing critical information
- Return ONLY valid JSON

OUTPUT FORMAT:
{{
  "verified": true,
  "confidence": "high | medium | low",
  "issues": [
    {{"drug": "drug_name", "issue": "description", "severity": "critical|warning|info"}}
  ],
  "dosage_checks": [
    {{"drug": "drug_name", "extracted_dose": "500mg", "typical_range": "250-1000mg", "status": "ok|high|low|unclear"}}
  ],
  "extraction_quality": "good | partial | poor",
  "notes": "Additional notes for the pharmacist"
}}

Return ONLY the JSON.
"""


# ── Public Functions ──────────────────────────────────────────────────────────

async def extract_drugs(image_bytes: bytes) -> dict:
    """
    Send prescription image bytes to Gemini Vision.
    Returns structured drug list and metadata.
    """
    try:
        img_part = {"mime_type": "image/jpeg", "data": image_bytes}
        response = model.generate_content([_EXTRACT_PROMPT, img_part])
        result   = _parse_json(response.text)
        if not result:
            return {
                "drug_list": [],
                "raw_text":  response.text,
                "error":     "Could not parse Gemini response as JSON",
            }
        return result
    except Exception as e:
        return {"drug_list": [], "raw_text": "", "error": str(e)}


async def explain_prescription(drugs: dict, interactions: list) -> dict:
    """
    Generate bilingual (English + Roman Urdu) explanation.
    Includes warnings, tips, and a one-sentence summary.
    """
    try:
        prompt   = _EXPLAIN_TEMPLATE.format(
            drugs=json.dumps(drugs.get("drug_list", []), indent=2),
            interactions=json.dumps(interactions, indent=2),
        )
        response = model.generate_content(prompt)
        result   = _parse_json(response.text)
        if not result:
            return {
                "english":  response.text,
                "urdu":     "",
                "warnings": [],
                "tips":     [],
                "summary":  "",
            }
        return result
    except Exception as e:
        return {"english": str(e), "urdu": "", "warnings": [], "tips": [], "summary": ""}


async def get_recommendations(drugs: dict, interactions: list) -> dict:
    """
    Return AI-powered medicine alternatives, supplements, dietary
    and lifestyle advice tailored for Pakistani patients.
    """
    try:
        prompt   = _RECOMMEND_TEMPLATE.format(
            drugs=json.dumps(drugs.get("drug_list", []), indent=2),
            interactions=json.dumps(interactions, indent=2),
        )
        response = model.generate_content(prompt)
        result   = _parse_json(response.text)
        if not result:
            return {
                "alternatives": [],
                "supplements":  [],
                "dietary":      [],
                "lifestyle":    [],
                "urgency":      "normal",
            }
        return result
    except Exception as e:
        return {
            "alternatives": [],
            "supplements":  [],
            "dietary":      [],
            "lifestyle":    [],
            "urgency":      "normal",
            "error":        str(e),
        }


async def double_check_prescription(drugs: dict) -> dict:
    """
    Verify extracted drug data for patient safety.
    Checks dosage ranges, flags OCR errors, scores extraction quality.
    """
    try:
        prompt   = _DOUBLE_CHECK_TEMPLATE.format(
            drugs=json.dumps(drugs.get("drug_list", []), indent=2)
        )
        response = model.generate_content(prompt)
        result   = _parse_json(response.text)
        if not result:
            return {
                "verified":           False,
                "confidence":         "low",
                "issues":             [],
                "dosage_checks":      [],
                "extraction_quality": "poor",
                "notes":              response.text,
            }
        return result
    except Exception as e:
        return {
            "verified":           False,
            "confidence":         "low",
            "issues":             [],
            "dosage_checks":      [],
            "extraction_quality": "poor",
            "notes":              str(e),
        }
