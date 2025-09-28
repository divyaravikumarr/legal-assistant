import json
import os
import re
from typing import List, Tuple
from models import Clause
import spacy

# ---------- spaCy setup ----------
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None

# ---------- Headings ----------
EN_HEADINGS = [
    "Definitions","Term","Term and Termination","Termination","Payment","Payment Terms","Fees",
    "Confidentiality","Intellectual Property","IP","Indemnity","Limitation of Liability","Liability",
    "Governing Law","Jurisdiction","Dispute Resolution","Arbitration","Non-Compete","Non Solicitation",
    "Force Majeure","Scope","Services","Deliverables"
]
HI_HEADINGS = [
    "परिभाषाएँ","अवधि","समापन","भुगतान","गोपनीयता","बौद्धिक संपदा","क्षतिपूर्ति",
    "देयता की सीमा","प्रवर्तनीय क़ानून","अधिकार क्षेत्र","विवाद निपटान","मध्यस्थता","बलपूर्वक"
]

H_WORDS = EN_HEADINGS + HI_HEADINGS
H_ALT = "|".join([re.escape(h) for h in H_WORDS])

STRONG_HEAD_RE = re.compile(
    rf"(?m)^(?P<head>(?:\d{{1,2}}\s*[\.\)\-]\s*)?(?:{H_ALT}))\b",
    re.I,
)
LOOSE_HEAD_RE = re.compile(
    rf"(?P<head>(?:\d{{1,2}}\s*[\.\)\-]\s*)?(?:{H_ALT}))\b",
    re.I,
)

DEVNAGARI_RE = re.compile(r"[\u0900-\u097F]")

def is_hindi(text: str) -> bool:
    return bool(DEVNAGARI_RE.search(text))

def cleanup_heading(h: str) -> str:
    h = re.sub(r"^\d{1,2}\s*[\.\)\-]\s*", "", h or "")
    h = re.sub(r"\s+", " ", h).strip()
    return h.title()

def normalize_whitespace(t: str) -> str:
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    t = re.sub(r"[ \t]+", " ", t)
    return t

# ---------- Clause detection ----------
def _split_by_matches(text: str, matches: List[re.Match]) -> List[Clause]:
    blocks = []
    for i, m in enumerate(matches):
        start = m.start()
        raw_title = m.group("head")
        title = cleanup_heading(raw_title)
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        body = body[len(raw_title):].lstrip(" :-\n\r\t")

        if blocks and blocks[-1].title == title:
            prev = blocks[-1]
            prev.text = (prev.text + "\n" + body).strip()
        else:
            blocks.append(Clause(id=f"c{i+1}", title=title, text=body))
    return blocks

def detect_clauses(text: str) -> List[Clause]:
    text = normalize_whitespace(text)

    strong = list(STRONG_HEAD_RE.finditer(text))
    if strong:
        blocks = _split_by_matches(text, strong)
        if blocks: return blocks

    loose = list(LOOSE_HEAD_RE.finditer(text))
    if loose:
        blocks = _split_by_matches(text, loose)
        filtered: List[Clause] = []
        for b in blocks:
            if len(b.text) < 40 and len(blocks) > 1:
                continue
            filtered.append(b)
        if filtered: return filtered

    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, buf = [], []
    for p in paras:
        buf.append(p)
        if len(buf) >= 3:
            chunks.append("\n\n".join(buf)); buf = []
    if buf: chunks.append("\n\n".join(buf))
    if chunks:
        return [Clause(id=f"p{i+1}", title=f"Clause {i+1}", text=c) for i, c in enumerate(chunks)]

    if nlp:
        doc = nlp(text)
        sents = [s.text.strip() for s in doc.sents if s.text.strip()]
        if sents:
            return [Clause(id=f"s{i+1}", title=f"Clause {i+1}", text=s) for i, s in enumerate(sents)]

    return [Clause(id="c1", title="Contract", text=text)]

# ---------- Entity extraction ----------
def extract_entities(clause_text: str) -> List[str]:
    if not nlp:
        return []
    doc = nlp(clause_text)
    ents = []
    for ent in doc.ents:
        if ent.label_ in ["DATE", "MONEY", "ORG", "GPE"]:
            ents.append(f"{ent.text} ({ent.label_})")
    return ents

# ---------- Heuristics (gentler) ----------
DAYS_RE   = re.compile(r"(?:within|net)?\s*(\d{2,3})\s*day", re.I)
NOTICE_RE = re.compile(r"notice(?:\s*period)?\s*(\d{1,2})\s*day", re.I)

# Default (calmer) weights. You can override via rules/risks.json.
DEFAULT_WEIGHTS = {
    "liability_disclaimed":    10,  # keep truly critical as red
    "unlimited_liability":      6,
    "unilateral_indemnity":     4,
    "liability_cap_missing":    2,
    "payment_terms_gt_45d":     2,
    "no_late_fee":              1,
    "unilateral_termination":   2,
    "short_notice":             1,
    "non_indian_law":           2,
    "foreign_forum":            1,
    "confidentiality_perpetual":2,
}

def _load_weights() -> dict:
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rules", "risks.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f) or {}
        # merge with defaults to avoid missing keys
        merged = DEFAULT_WEIGHTS.copy()
        merged.update({k:int(v) for k,v in data.items()})
        return merged
    except Exception:
        return DEFAULT_WEIGHTS.copy()

WEIGHTS = _load_weights()

SEVERE_FLAGS = {"liability_disclaimed", "unlimited_liability"}

def apply_rules(cl: Clause) -> Tuple[int, List[str]]:
    hits: List[str] = []
    t = cl.text.lower()

    # Indemnity
    if "indemn" in t or "क्षतिपूर्ति" in t:
        if not any(s in t for s in ["each party", "mutual", "दोनों पक्ष"]):
            hits.append("unilateral_indemnity")
        if any(s in t for s in ["without limit", "unlimited", "no limit", "असीमित"]):
            hits.append("unlimited_liability")

    # Liability
    if "liability" in t or "देयता" in t:
        if "no liability" in t or "shall have no liability" in t:
            hits.append("liability_disclaimed")
        if any(s in t for s in ["unlimited","without limit","no limit","असीमित"]):
            hits.append("unlimited_liability")
        # only flag cap missing if there is *no* sign of a cap anywhere
        if not any(s in t for s in ["cap", "maximum", "limit of", "capped", "सीमा"]):
            hits.append("liability_cap_missing")

    # Payment terms
    if any(w in t for w in ["payment","fees","invoice","भुगतान","शुल्क"]):
        m = DAYS_RE.search(t)
        if m:
            try:
                if int(m.group(1)) > 45:
                    hits.append("payment_terms_gt_45d")
            except Exception:
                pass
        if not any(w in t for w in ["late fee", "interest", "विलंब"]):
            hits.append("no_late_fee")

    # Termination
    if "termination" in t or "समापन" in t:
        if ("for convenience" in t or "may terminate" in t) and not any(w in t for w in ["either party","client","both parties","दोनों"]):
            hits.append("unilateral_termination")
        m = NOTICE_RE.search(t)
        if m:
            try:
                if int(m.group(1)) < 15:
                    hits.append("short_notice")
            except Exception:
                pass

    # Governing law / jurisdiction
    if any(w in t for w in ["governing law","jurisdiction","प्रवर्तनीय","अधिकार क्षेत्र"]):
        if not any(w in t for w in ["india","भारतीय","भारत"]):
            hits.append("non_indian_law")
        if any(city in t for city in ["delaware","new york","california","singapore","london"]):
            hits.append("foreign_forum")

    # Confidentiality
    if "confidential" in t or "गोपनीय" in t:
        if any(w in t for w in ["perpetual","indefinite"]) or ("अवधि" in t and "हमेशा" in t):
            hits.append("confidentiality_perpetual")

    # ---------- Scoring with dampeners ----------
    raw = sum(WEIGHTS.get(h, 0) for h in hits)

    # Dampeners (reduce noise / reward good signals)
    dampen = 0
    # Mutual language reduces indemnity/severity noise
    if any(w in t for w in ["mutual", "each party", "दोनों पक्ष"]):
        dampen += 2
    # Explicit caps reduce liability risk
    if any(w in t for w in ["cap of", "capped at", "maximum liability", "aggregate cap"]):
        dampen += 2
    # Reasonableness language softens absolute clauses
    if "reasonable" in t or "commercially reasonable" in t:
        dampen += 1
    # Balanced termination text
    if "either party may terminate" in t:
        dampen += 2

    raw = max(0, raw - dampen)

    # Soft cap: unless a severe flag is present, don't let small issues exceed 6/10
    if not any(f in hits for f in SEVERE_FLAGS):
        raw = min(raw, 6)

    # Final clamp to 0..10
    score = max(0, min(10, int(raw)))

    return score, hits
