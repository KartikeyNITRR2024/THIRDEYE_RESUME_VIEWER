# """
# ATS-safe resume PDF generator.
# Input: compact JSON dict (schema: n,t,c,sm,sk,ex,ed,ach)
# Output: single-column, plain-text PDF that ATS parsers can read reliably.
# """

# import re
# from reportlab.lib.pagesizes import A4
# from reportlab.lib.units import mm
# from reportlab.lib.enums import TA_LEFT
# from reportlab.lib.styles import ParagraphStyle
# from reportlab.platypus import SimpleDocTemplate, Paragraph
# from reportlab.lib.colors import HexColor

# def build_styles():
#     return {
#         "name": ParagraphStyle("name", fontName="Helvetica-Bold", fontSize=18,
#                                leading=22, alignment=TA_LEFT, spaceAfter=2),
#         "title": ParagraphStyle("title", fontName="Helvetica", fontSize=11,
#                                 leading=14, textColor=HexColor("#333333"), spaceAfter=2),
#         "contact": ParagraphStyle("contact", fontName="Helvetica", fontSize=9.5,
#                                   leading=12, textColor=HexColor("#444444"), spaceAfter=10),
#         "section": ParagraphStyle("section", fontName="Helvetica-Bold", fontSize=12,
#                                   leading=16, spaceBefore=10, spaceAfter=4,
#                                   textColor=HexColor("#000000")),
#         "body": ParagraphStyle("body", fontName="Helvetica", fontSize=10,
#                                leading=14, spaceAfter=4, alignment=TA_LEFT),
#         "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=10,
#                                  leading=14, leftIndent=12, spaceAfter=2),
#         "jobheader": ParagraphStyle("jobheader", fontName="Helvetica-Bold", fontSize=10.5,
#                                     leading=14, spaceBefore=6, spaceAfter=1),
#         "jobmeta": ParagraphStyle("jobmeta", fontName="Helvetica-Oblique", fontSize=9.5,
#                                   leading=12, spaceAfter=3, textColor=HexColor("#555555")),
#     }

# def make_links_clickable(contact_str: str) -> str:
#     """
#     Parses the pipe-separated contact string and wraps emails and URLs 
#     in reportlab-compatible HTML link tags.
#     """
#     if not contact_str:
#         return ""
    
#     parts = [p.strip() for p in contact_str.split("|")]
#     formatted_parts = []
    
#     for part in parts:
#         # Check for Email
#         if "@" in part and "." in part:
#             formatted_parts.append(f'<a href="mailto:{part}" color="blue">{part}</a>')
#         # Check for typical URLs (linkedin, github, leetcode, etc.)
#         elif ".com" in part or ".in" in part or "github." in part:
#             url = part if part.startswith("http") else f"https://{part}"
#             formatted_parts.append(f'<a href="{url}" color="blue">{part}</a>')
#         else:
#             # Leave normal text (like phone numbers or locations) as is
#             formatted_parts.append(part)
            
#     return " | ".join(formatted_parts)


# def generate_resume_pdf(data: dict, output_path: str) -> str:
#     styles = build_styles()
#     doc = SimpleDocTemplate(
#         output_path, pagesize=A4,
#         leftMargin=20 * mm, rightMargin=20 * mm,
#         topMargin=15 * mm, bottomMargin=15 * mm,
#         title=data.get("n", "Resume"),
#     )

#     story = []

#     # --- HEADER ---
#     story.append(Paragraph(data.get("n", ""), styles["name"]))
#     if data.get("t"):
#         story.append(Paragraph(data["t"], styles["title"]))
#     if data.get("c"):
#         # Make the links clickable before adding to story
#         clickable_contact = make_links_clickable(data["c"])
#         story.append(Paragraph(clickable_contact, styles["contact"]))

#     # --- SUMMARY ---
#     if data.get("sm"):
#         story.append(Paragraph("SUMMARY", styles["section"]))
#         story.append(Paragraph(data["sm"], styles["body"]))

#     # --- SKILLS ---
#     if data.get("sk"):
#         story.append(Paragraph("SKILLS", styles["section"]))
#         story.append(Paragraph(" | ".join(data["sk"]), styles["body"]))

#     # --- EXPERIENCE ---
#     if data.get("ex"):
#         story.append(Paragraph("EXPERIENCE", styles["section"]))
#         for job in data["ex"]:
#             header = f'{job.get("r","")} — {job.get("c","")}'
#             story.append(Paragraph(header, styles["jobheader"]))
#             if job.get("d"):
#                 story.append(Paragraph(job["d"], styles["jobmeta"]))
#             for b in job.get("b", []):
#                 story.append(Paragraph(f"• {b}", styles["bullet"]))

#     # --- EDUCATION ---
#     if data.get("ed"):
#         story.append(Paragraph("EDUCATION", styles["section"]))
#         for e in data["ed"]:
#             line = f'{e.get("g","")}, {e.get("s","")} ({e.get("y","")})'
#             story.append(Paragraph(line, styles["body"]))

#     # --- ACHIEVEMENTS ---
#     if data.get("ach"):
#         story.append(Paragraph("ACHIEVEMENTS", styles["section"]))
#         for ach in data["ach"]:
#             story.append(Paragraph(f"• {ach}", styles["bullet"]))

#     doc.build(story)
#     return output_path

"""
ATS-safe resume PDF generator (robust version).
Input: compact JSON dict (schema: n,t,c,sm,sk,ex,ed,ach)
Output: single-column, plain-text PDF that ATS parsers can read reliably,
        while still looking clean for a human reviewer.

Design goals for this version:
  1. Never crash on missing / malformed / wrong-type data.
  2. Stay ATS-safe (single column, real text, no icon-only content).
  3. Slightly nicer for human readers (subtle color, spacing, dividers)
     without introducing tables/columns that break ATS parsing.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.colors import HexColor
from xml.sax.saxutils import escape


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

def build_styles():
    return {
        "name": ParagraphStyle("name", fontName="Helvetica-Bold", fontSize=18,
                               leading=22, alignment=TA_LEFT, spaceAfter=2,
                               textColor=HexColor("#1a1a1a")),
        "title": ParagraphStyle("title", fontName="Helvetica", fontSize=11,
                                leading=14, textColor=HexColor("#333333"), spaceAfter=2),
        "contact": ParagraphStyle("contact", fontName="Helvetica", fontSize=9.5,
                                  leading=12, textColor=HexColor("#444444"), spaceAfter=8),
        "section": ParagraphStyle("section", fontName="Helvetica-Bold", fontSize=12,
                                  leading=16, spaceBefore=10, spaceAfter=3,
                                  textColor=HexColor("#1a1a1a")),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=10,
                               leading=14, spaceAfter=4, alignment=TA_LEFT,
                               textColor=HexColor("#222222")),
        "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=10,
                                 leading=14, leftIndent=12, spaceAfter=2,
                                 textColor=HexColor("#222222")),
        "jobheader": ParagraphStyle("jobheader", fontName="Helvetica-Bold", fontSize=10.5,
                                    leading=14, spaceBefore=6, spaceAfter=1,
                                    textColor=HexColor("#1a1a1a")),
        "jobmeta": ParagraphStyle("jobmeta", fontName="Helvetica-Oblique", fontSize=9.5,
                                  leading=12, spaceAfter=3, textColor=HexColor("#555555")),
        "fallback": ParagraphStyle("fallback", fontName="Helvetica-Oblique", fontSize=9,
                                   leading=12, textColor=HexColor("#888888")),
    }


# ---------------------------------------------------------------------------
# Small safe helpers - every one of these is defensive against None,
# wrong types, empty strings, missing keys, etc.
# ---------------------------------------------------------------------------

def _s(value, default=""):
    """Safely coerce anything to a stripped string."""
    if value is None:
        return default
    try:
        text = str(value).strip()
    except Exception:
        return default
    return text if text else default


def _safe_list(value):
    """Return a usable list even if input is None, a string, a dict, etc."""
    if value is None:
        return []
    if isinstance(value, list):
        return [v for v in value if v is not None]
    if isinstance(value, (tuple, set)):
        return [v for v in value if v is not None]
    if isinstance(value, str):
        # tolerate a comma-separated string being passed where a list was expected
        return [p.strip() for p in value.split(",") if p.strip()]
    # single scalar/dict passed where a list was expected -> wrap it
    return [value]


def _esc(text):
    """Escape text for ReportLab's mini-XML markup so stray <, &, > in
    real user data (e.g. 'C++', 'R&D', '<Confidential>') can't break
    rendering or raise a parse error."""
    return escape(_s(text))


def safe_paragraph(text, style, styles_map=None):
    """Build a Paragraph, but if ReportLab's XML parser ever chokes on the
    markup (e.g. an unbalanced tag slipped in), fall back to a fully
    escaped plain-text version instead of raising at runtime."""
    try:
        return Paragraph(text, style)
    except Exception:
        fallback_style = (styles_map or {}).get("fallback", style)
        try:
            return Paragraph(escape(_s(text)), fallback_style)
        except Exception:
            # absolute last resort - never let a single line kill the whole PDF
            return Paragraph("(content omitted due to formatting error)", fallback_style)


# ---------------------------------------------------------------------------
# Contact line -> clickable links, defensively
# ---------------------------------------------------------------------------

def make_links_clickable(contact_str) -> str:
    contact_str = _s(contact_str)
    if not contact_str:
        return ""

    parts = [p.strip() for p in contact_str.split("|") if p.strip()]
    formatted_parts = []

    url_hint_tlds = (".com", ".in", ".io", ".dev", ".co", ".org", ".net")

    for part in parts:
        try:
            if "@" in part and "." in part and " " not in part:
                formatted_parts.append(
                    f'<a href="mailto:{_esc(part)}" color="blue">{_esc(part)}</a>'
                )
            elif ("github." in part or "linkedin." in part or part.startswith("http")
                  or any(tld in part for tld in url_hint_tlds)):
                url = part if part.startswith("http") else f"https://{part}"
                formatted_parts.append(f'<a href="{_esc(url)}" color="blue">{_esc(part)}</a>')
            else:
                formatted_parts.append(_esc(part))
        except Exception:
            # if anything about this one part goes wrong, keep the rest intact
            formatted_parts.append(_esc(part))

    return " | ".join(formatted_parts) if formatted_parts else ""


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------

def generate_resume_pdf(data: dict, output_path: str) -> str:
    """
    Builds the resume PDF. Guaranteed not to raise on missing/partial/odd
    data - sections with no usable content are simply skipped, and
    malformed nested items are skipped individually rather than aborting
    the whole document.
    """
    if not isinstance(data, dict):
        data = {}

    styles = build_styles()

    try:
        doc = SimpleDocTemplate(
            output_path, pagesize=A4,
            leftMargin=20 * mm, rightMargin=20 * mm,
            topMargin=15 * mm, bottomMargin=15 * mm,
            title=_s(data.get("n"), "Resume"),
        )
    except Exception:
        # extremely defensive fallback in case title metadata itself misbehaves
        doc = SimpleDocTemplate(
            output_path, pagesize=A4,
            leftMargin=20 * mm, rightMargin=20 * mm,
            topMargin=15 * mm, bottomMargin=15 * mm,
        )

    story = []

    # --- HEADER ---
    name = _s(data.get("n"), "Your Name")
    story.append(safe_paragraph(_esc(name), styles["name"], styles))

    title = _s(data.get("t"))
    if title:
        story.append(safe_paragraph(_esc(title), styles["title"], styles))

    contact_raw = data.get("c")
    clickable_contact = make_links_clickable(contact_raw)
    if clickable_contact:
        story.append(safe_paragraph(clickable_contact, styles["contact"], styles))

    # thin divider - purely visual, still just a line, doesn't affect text extraction
    story.append(HRFlowable(width="100%", thickness=0.6, color=HexColor("#cccccc"),
                             spaceBefore=2, spaceAfter=8))

    # --- SUMMARY ---
    summary = _s(data.get("sm"))
    if summary:
        story.append(safe_paragraph("SUMMARY", styles["section"], styles))
        story.append(safe_paragraph(_esc(summary), styles["body"], styles))

    # --- SKILLS ---
    skills = [_s(s) for s in _safe_list(data.get("sk"))]
    skills = [s for s in skills if s]
    if skills:
        story.append(safe_paragraph("SKILLS", styles["section"], styles))
        story.append(safe_paragraph(_esc(" | ".join(skills)), styles["body"], styles))

    # --- EXPERIENCE ---
    experience = _safe_list(data.get("ex"))
    valid_jobs = []
    for job in experience:
        if not isinstance(job, dict):
            continue
        role = _s(job.get("r"))
        company = _s(job.get("c"))
        if not role and not company:
            continue  # nothing usable in this entry, skip it silently
        valid_jobs.append(job)

    if valid_jobs:
        story.append(safe_paragraph("EXPERIENCE", styles["section"], styles))
        for job in valid_jobs:
            role = _s(job.get("r"), "")
            company = _s(job.get("c"), "")
            if role and company:
                header = f"{role} — {company}"
            else:
                header = role or company  # only one of them present

            story.append(safe_paragraph(_esc(header), styles["jobheader"], styles))

            date_loc = _s(job.get("d"))
            if date_loc:
                story.append(safe_paragraph(_esc(date_loc), styles["jobmeta"], styles))

            bullets = [_s(b) for b in _safe_list(job.get("b"))]
            for b in bullets:
                if b:
                    story.append(safe_paragraph(f"- {_esc(b)}", styles["bullet"], styles))

    # --- EDUCATION ---
    education = _safe_list(data.get("ed"))
    valid_edu = []
    for e in education:
        if not isinstance(e, dict):
            continue
        grade = _s(e.get("g"))
        school = _s(e.get("s"))
        year = _s(e.get("y"))
        if not (grade or school or year):
            continue
        valid_edu.append((grade, school, year))

    if valid_edu:
        story.append(safe_paragraph("EDUCATION", styles["section"], styles))
        for grade, school, year in valid_edu:
            bits = [b for b in (grade, school) if b]
            line = ", ".join(bits) if bits else "Education"
            if year:
                line += f" ({year})"
            story.append(safe_paragraph(_esc(line), styles["body"], styles))

    # --- ACHIEVEMENTS ---
    achievements = [_s(a) for a in _safe_list(data.get("ach"))]
    achievements = [a for a in achievements if a]
    if achievements:
        story.append(safe_paragraph("ACHIEVEMENTS", styles["section"], styles))
        for ach in achievements:
            story.append(safe_paragraph(f"- {_esc(ach)}", styles["bullet"], styles))

    # Guarantee the document is never completely empty (ReportLab can error
    # on a zero-flowable story in some edge cases, and an empty PDF is
    # useless to the user anyway).
    if len(story) <= 1:
        story.append(Spacer(1, 4))
        story.append(safe_paragraph(
            "No resume content was provided.", styles["body"], styles))

    try:
        doc.build(story)
    except Exception as e:
        # last-resort fallback: build a minimal, guaranteed-valid PDF so the
        # function never raises at runtime, and surface what happened.
        minimal_story = [
            safe_paragraph(_esc(name), styles["name"], styles),
            Spacer(1, 8),
            safe_paragraph(
                "This resume could not be fully formatted due to an internal "
                "error and was generated with reduced content.",
                styles["fallback"], styles
            ),
        ]
        try:
            doc.build(minimal_story)
        except Exception:
            # if even this fails, there's nothing more we can safely do;
            # re-raise so the caller is aware the file was not produced.
            raise RuntimeError(f"Failed to generate resume PDF: {e}") from e

    return output_path


# ---------------------------------------------------------------------------
# Manual test / demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    good = {
        "n": "Jordan Patel",
        "t": "Senior Data Analyst",
        "c": "jordan.patel@example.com | +91 98765 43210 | linkedin.com/in/jordanpatel | github.com/jpatel",
        "sm": "Data analyst with 5 years of experience in SQL, Python, and dashboarding.",
        "sk": ["SQL", "Python", "Tableau", "Power BI", "Excel"],
        "ex": [{
            "r": "Senior Data Analyst", "c": "Acme Corp",
            "d": "Jan 2022 - Present, Mumbai",
            "b": ["Built automated reporting pipelines reducing manual work by 40%",
                  "Led a team of 3 analysts on quarterly business reviews"],
        }],
        "ed": [{"g": "B.Tech Computer Science", "s": "IIT Bombay", "y": "2019"}],
        "ach": ["Employee of the Year 2023", "Published 2 internal whitepapers"],
    }

    # deliberately broken / partial inputs to prove nothing crashes
    messy_cases = [
        {},                                              # completely empty
        {"n": None, "c": None, "sk": None, "ex": None},  # all None
        {"n": "Riya Shah", "sk": "SQL, Python, Excel"},   # skills as a string not list
        {"n": "Sam <script> & Co", "t": "R&D <Lead>"},    # special XML chars
        {"n": "Kabir", "ex": [{"r": "Engineer"}, {"b": ["orphan bullet, no role/company"]}, "not a dict"]},
        {"n": "Meera", "ed": [{"y": "2020"}, {}]},        # partial education entries
        good,
    ]

    for i, case in enumerate(messy_cases):
        out = f"/home/claude/test_resume_{i}.pdf"
        generate_resume_pdf(case, out)
        print(f"case {i}: OK -> {out}")