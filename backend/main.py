# path: backend/main.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, PlainTextResponse
from ingest import extract_text
from analysis import analyze_contract
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from html import escape
from datetime import datetime
import json, time

app = FastAPI(title="Legal Assistant API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...), options: str = Form("{}")):
    t0 = time.time()
    try:
        opts = json.loads(options or "{}")
    except Exception:
        opts = {}

    max_pages = int(opts.get("max_pages", 20))
    text, _ = extract_text(file, max_pages=max_pages, max_chars=60_000)

    if not text.strip():
        return {
            "overall_score": 0,
            "bucket": "Low",
            "duration_ms": int((time.time() - t0) * 1000),
            "top_risks": [],
            "clauses": [],
        }

    res = analyze_contract(text, opts)
    res["duration_ms"] = int((time.time() - t0) * 1000)
    return res

# ---------- Simple Markdown (for .md export) ----------
def build_markdown(payload: dict) -> str:
    md = []
    md.append("# Contract Analysis Report\n")
    md.append(f"**Overall score:** {payload.get('overall_score','-')}/10  \n")
    md.append(f"**Bucket:** {payload.get('bucket','-')}  \n")
    md.append(f"**Duration:** {payload.get('duration_ms','-')} ms\n")

    top = payload.get("top_risks", [])
    if top:
        md.append("\n## Top Risks\n")
        for r in top:
            line = f"- **{r.get('title','')}** — {r.get('score','')}/10"
            reason = r.get("reason")
            if reason:
                line += f"\n  {reason}"
            md.append(line)

    # Keep the md short; PDF has the full details
    return "\n".join(md)

@app.post("/report", response_class=PlainTextResponse)
async def report(payload: dict):
    md = build_markdown(payload)
    return PlainTextResponse(md, media_type="text/markdown; charset=utf-8")

# ---------- Styled PDF Report (safe + wrapped) ----------
@app.post("/report/pdf")
async def report_pdf(payload: dict):
    """
    Generate a professional PDF report with margins, wrapping, tables, and safe text.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=60,
        bottomMargin=40,
    )

    # Base styles
    styles = getSampleStyleSheet()
    # Use unique style names to avoid "already defined" errors
    styles.add(ParagraphStyle(name="H1Report", fontSize=18, leading=22, spaceAfter=12,
                              textColor=colors.HexColor("#1E3A8A"), alignment=1))
    styles.add(ParagraphStyle(name="H2Section", fontSize=14, leading=18, spaceAfter=8,
                              textColor=colors.HexColor("#111827"), spaceBefore=6))
    styles.add(ParagraphStyle(name="BodySmall", fontSize=10, leading=14, spaceAfter=6))
    styles.add(ParagraphStyle(name="MetaSmall", fontSize=9, textColor=colors.grey, leading=12))

    story = []

    # --- Cover Page ---
    story.append(Paragraph("Contract Analysis Report", styles["H1Report"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%d %B %Y, %H:%M:%S')}", styles["MetaSmall"]))
    story.append(PageBreak())

    # --- Summary ---
    story.append(Paragraph("Summary", styles["H1Report"]))
    story.append(Spacer(1, 8))

    data = [
        ["Overall Score", f"{escape(str(payload.get('overall_score','-')))} / 10"],
        ["Risk Bucket", escape(str(payload.get("bucket","-")))],
        ["Duration", f"{escape(str(payload.get('duration_ms','-')))} ms"],
    ]
    summary_table = Table(data, colWidths=[150, 250])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F3F4F6")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 16))

    # --- Top Risks (Table) ---
    top = payload.get("top_risks", []) or []
    if top:
        story.append(Paragraph("Top Risks", styles["H1Report"]))
        story.append(Spacer(1, 8))

        risk_data = [["Clause Title", "Score", "Reason"]]
        for r in top:
            risk_data.append([
                escape(str(r.get("title", "-"))),
                escape(str(r.get("score", "-"))),
                escape(str(r.get("reason", "-"))),
            ])
        risk_table = Table(risk_data, colWidths=[180, 60, 200])
        risk_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ("FONTSIZE", (0, 0), (-1, 0), 11),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(risk_table)
        story.append(Spacer(1, 16))

    # --- Clauses ---
    clauses = payload.get("clauses", []) or []
    if clauses:
        story.append(Paragraph("Clauses", styles["H1Report"]))
        story.append(Spacer(1, 8))

        for c in clauses:
            title = escape(str(c.get("title", "Clause")))
            risk = int(c.get("risk", 0))
            # labels without emojis for font safety
            risk_label = "Safe" if risk == 0 else ("Low" if risk <= 3 else ("Medium" if risk <= 6 else "High"))
            story.append(Paragraph(f"{title} — {risk_label} ({risk}/10)", styles["H2Section"]))

            # Body text (escape + truncate)
            body_text = escape((c.get("text") or "")[:2000])
            if not body_text:
                body_text = "-"
            story.append(Paragraph(body_text, styles["BodySmall"]))
            story.append(Spacer(1, 4))

            # Rule hits / Entities
            hits = c.get("rule_hits") or []
            ents = c.get("entities") or []
            if hits:
                story.append(Paragraph("Rule hits: " + escape(", ".join(map(str, hits))), styles["BodySmall"]))
            if ents:
                story.append(Paragraph("Entities: " + escape(", ".join(map(str, ents))), styles["BodySmall"]))

            # LLM bits
            llm = c.get("llm") or {}
            expl = llm.get("explanation")
            issue = llm.get("issue")
            alt = llm.get("alt_clause")

            if expl:
                story.append(Paragraph("Explanation:", styles["BodySmall"]))
                story.append(Paragraph(escape(str(expl)), styles["BodySmall"]))
            if issue:
                story.append(Paragraph("Issue:", styles["BodySmall"]))
                story.append(Paragraph(escape(str(issue)), styles["BodySmall"]))
            if alt:
                story.append(Paragraph("Suggested Alternative:", styles["BodySmall"]))
                story.append(Paragraph(f"<font face='Courier'>{escape(str(alt)[:1000])}</font>", styles["BodySmall"]))

            story.append(Spacer(1, 14))

    # Build PDF
    try:
        doc.build(story)
    except Exception as e:
        # Return JSON error so frontend shows the real reason instead of a 500
        return PlainTextResponse(f"PDF generation failed: {e}", status_code=500)

    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=analysis_report.pdf"},
    )
