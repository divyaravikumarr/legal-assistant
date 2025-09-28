from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Clause(BaseModel):
    id: str
    title: str
    text: str
    risk: int = 0
    rule_hits: List[str] = []

class LLMNote(BaseModel):
    explanation: Optional[str] = None
    issue: Optional[str] = None
    alt_clause: Optional[str] = None
    risk_0_10: Optional[int] = None

class AnalysisOptions(BaseModel):
    lang: str = "English"
    max_pages: int = 20
    use_llm: bool = False

class TopRisk(BaseModel):
    title: str
    score: int
    reason: str

class AnalysisResult(BaseModel):
    overall_score: int
    bucket: str
    duration_ms: int
    top_risks: List[TopRisk] = []
    clauses: List[Dict[str, Any]] = []
