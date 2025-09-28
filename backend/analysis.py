import time
from typing import Dict, Any
from rules import detect_clauses, apply_rules, extract_entities
from llm import explain_clause  # LLM integration

DEFAULT_BUDGET_SEC = 15
MAX_LLM_CLAUSES = 20  # slightly higher since we now want all clauses, adjust if needed

def bucketize(s: int) -> str:
    if s <= 3: return "Low"
    if s <= 6: return "Medium"
    return "High"

def _short_summary(text: str, chars: int = 700) -> str:
    t = " ".join(text.split())
    return t[:chars]

def analyze_contract(text: str, options: Dict[str, Any]) -> Dict[str, Any]:
    start = time.time()
    budget = int(options.get("time_budget_sec", DEFAULT_BUDGET_SEC))
    lang = options.get("lang", "English")

    clauses = detect_clauses(text)
    contract_summary = _short_summary(text)

    out = []
    for cl in clauses:
        # Heuristic rules
        score, hits = apply_rules(cl)
        cl.risk, cl.rule_hits = score, hits

        clause_dict = cl.model_dump()
        clause_dict["entities"] = extract_entities(cl.text)

        # --- Always call LLM if enabled ---
        if options.get("use_llm"):
            remaining = budget - (time.time() - start)
            if remaining <= 3:
                break  # stop if close to time budget
            per_timeout = max(6, int(min(18, remaining - 1)))
            clause_dict["llm"] = explain_clause(
                clause_text=cl.text,
                title=cl.title,
                lang=lang,
                summary=contract_summary,
                timeout_sec=per_timeout
            )

        out.append(clause_dict)

        # Respect budget
        if time.time() - start > budget:
            break

    # Top risks (score >= 5)
    top = [
        {"title": c["title"], "score": c["risk"], "reason": ", ".join(c.get("rule_hits", [])) or "Rule risk"}
        for c in out if c.get("risk", 0) >= 5
    ]
    top = sorted(top, key=lambda x: x["score"], reverse=True)[:5]

    # Overall score = max of top-3 risks (or max of all if none flagged)
   # Overall score = weighted average of top-3 risks (0.6, 0.3, 0.1)
    all_scores = sorted((c.get("risk", 0) for c in out), reverse=True)
    a = all_scores[0] if len(all_scores) > 0 else 0
    b = all_scores[1] if len(all_scores) > 1 else 0
    c3 = all_scores[2] if len(all_scores) > 2 else 0
    overall = int(round(0.6 * a + 0.3 * b + 0.1 * c3))

    return {
        "overall_score": overall,
        "bucket": bucketize(overall),
        "duration_ms": int((time.time() - start) * 1000),
        "top_risks": top,
        "clauses": out,
    }
