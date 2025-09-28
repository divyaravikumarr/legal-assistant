from backend.rules import detect_clauses, apply_rules

def test_detect_basic():
    text = "Indemnity\nParty A indemnifies Party B.\n\nPayment\nNet 60 days."
    cs = detect_clauses(text)
    assert len(cs) >= 2

def test_apply_rules():
    from backend.models import Clause
    cl = Clause(id="1", title="Payment", text="Payment terms: Net 60 days. No late fee.")
    score, hits = apply_rules(cl)
    assert score >= 2
    assert "payment_terms_gt_45d" in hits
