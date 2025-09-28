import os, json
from typing import Dict, Optional
from dotenv import load_dotenv
from groq import Groq

# Load variables from .env
load_dotenv()

# --- Groq setup ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
_groq_client = None

def _get_groq():
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=GROQ_API_KEY)
    return _groq_client

# --- Prompts ---
SYSTEM_PROMPT = (
    "You are an Indian SME contract assistant. Analyze the clause below and respond in STRICT JSON.\n"
    "Keep it concise and practical for a business owner (<=120 words explanation). "
    "Use Indian legal context; do not give legal advice disclaimers.\n\n"
    "JSON schema:\n"
    "{\n"
    '  "explanation": str,\n'
    '  "issue": str|null,\n'
    '  "alt_clause": str|null,\n'
    '  "risk_0_10": int\n'
    "}\n"
)

USER_TEMPLATE = (
    "Language: {lang}\n"
    "Contract summary (short): {summary}\n"
    "Clause title: {title}\n"
    "Clause text:\n{clause}\n\n"
    "Return ONLY the JSON. No prose outside JSON."
)

# --- Main function ---
def explain_clause(clause_text: str, title: str, lang: str = "English",
                   summary: str = "", timeout_sec: int = 18) -> Dict:
    if not GROQ_API_KEY:
        return _missing_key()

    content = USER_TEMPLATE.format(
        lang=lang,
        summary=(summary or "")[:600],
        title=title or "Clause",
        clause=clause_text[:4000],
    )

    try:
        client = _get_groq()
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            temperature=0.2,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": content},
            ],
        )
        txt = resp.choices[0].message.content
        return _parse_response(txt)
    except Exception as e:
        return _error(str(e))

# --- Helpers ---
def _parse_response(txt: str) -> Dict:
    data = _safe_json(txt)
    return {
        "explanation": data.get("explanation") or "",
        "issue": data.get("issue"),
        "alt_clause": data.get("alt_clause"),
        "risk_0_10": _safe_int(data.get("risk_0_10")),
    }

def _safe_json(s: str) -> Dict:
    if not s:
        return {}
    s = s.strip()
    start, end = s.find("{"), s.rfind("}")
    if start != -1 and end != -1 and end > start:
        s = s[start:end+1]
    try:
        return json.loads(s)
    except Exception:
        return {}

def _safe_int(x: Optional[int]) -> Optional[int]:
    try:
        if x is None:
            return None
        return max(0, min(10, int(x)))
    except Exception:
        return None

def _missing_key() -> Dict:
    return {
        "explanation": "⚠️ No Groq API key found. Showing heuristic results only.",
        "issue": None,
        "alt_clause": None,
        "risk_0_10": None,
    }

def _error(msg: str) -> Dict:
    return {
        "explanation": f"⚠️ LLM error: {msg}",
        "issue": None,
        "alt_clause": None,
        "risk_0_10": None,
    }
