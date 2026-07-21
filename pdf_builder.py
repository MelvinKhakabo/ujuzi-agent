"""
UJUZI AGENT — PDF Builder
──────────────────────────
Role: Post-processing step. Reads teacher_content, student_content,
and video_resources from session state and assembles clean PDFs
using reportlab.

Run automatically after the pipeline completes.
Output files land in the /output folder.

No LLM calls. Pure Python.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# ── Colour palette ─────────────────────────────────────────────────────────
TEAL       = HexColor("#0D7377")
TEAL_LITE  = HexColor("#E8F5F5")
DARK       = HexColor("#2B2B2B")
MID        = HexColor("#555555")
MUTED      = HexColor("#888888")
LIGHT      = HexColor("#F1EFE8")
GOLD       = HexColor("#D4A017")


def build_styles():
    """Define all paragraph styles used in the PDFs."""
    base = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "title",
            fontName="Helvetica-Bold",
            fontSize=22,
            textColor=TEAL,
            spaceAfter=6,
            leading=28,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            fontName="Helvetica",
            fontSize=13,
            textColor=MID,
            spaceAfter=4,
        ),
        "section_header": ParagraphStyle(
            "section_header",
            fontName="Helvetica-Bold",
            fontSize=13,
            textColor=white,
            spaceBefore=14,
            spaceAfter=4,
            leading=16,
            backColor=TEAL,
            leftIndent=-12,
            rightIndent=-12,
            borderPadding=(4, 12, 4, 12),
        ),
        "subsection": ParagraphStyle(
            "subsection",
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=TEAL,
            spaceBefore=10,
            spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Helvetica",
            fontSize=10,
            textColor=DARK,
            spaceAfter=4,
            leading=15,
        ),
        "body_indent": ParagraphStyle(
            "body_indent",
            fontName="Helvetica",
            fontSize=10,
            textColor=DARK,
            spaceAfter=3,
            leading=15,
            leftIndent=16,
        ),
        "note": ParagraphStyle(
            "note",
            fontName="Helvetica-Oblique",
            fontSize=9,
            textColor=MID,
            spaceAfter=3,
            leading=13,
            leftIndent=8,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontName="Helvetica",
            fontSize=8,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
    }
    return styles


def add_header_block(story, styles, title, subtitle, doc_type, country, level):
    """Adds the coloured header block at the top of each PDF."""
    story.append(Spacer(1, 0.3 * cm))

    # Type badge
    badge_color = TEAL if doc_type == "TEACHER LESSON PLAN" else GOLD
    story.append(Paragraph(doc_type, ParagraphStyle(
        "badge",
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=white,
        backColor=badge_color,
        spaceAfter=6,
        borderPadding=(3, 8, 3, 8),
    )))

    story.append(Paragraph(title, styles["title"]))
    story.append(Paragraph(f"{level}  ·  {country}", styles["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=2, color=TEAL, spaceAfter=12))


def parse_content_to_story(content_text, styles):
    """
    Converts the plain-text content from the Content Builder agent
    into a list of reportlab flowables.

    Parses the structured text format the Content Builder produces:
    - ALL CAPS lines with dashes → section headers
    - Lines starting with → or - → indented body
    - Lines starting with Slide N → subsection headers
    - Everything else → body text
    """
    story = []
    lines = content_text.strip().split("\n")

    for line in lines:
        stripped = line.strip()

        if not stripped:
            story.append(Spacer(1, 0.2 * cm))
            continue

        # Section headers: ALL CAPS lines (with optional dashes)
        if (stripped.isupper() and len(stripped) > 3) or \
           (stripped.replace("─", "").replace("-", "").replace(" ", "").isupper()
            and len(stripped.replace("─", "").replace("-", "").strip()) > 3):
            # Skip pure separator lines
            if set(stripped).issubset(set("─ -─")):
                story.append(HRFlowable(width="100%", thickness=0.5,
                                         color=LIGHT, spaceAfter=4))
                continue
            story.append(Paragraph(stripped, styles["section_header"]))
            continue

        # Slide headers
        if stripped.lower().startswith("slide ") and "—" in stripped:
            story.append(Paragraph(stripped, styles["subsection"]))
            continue

        # Indented items
        if stripped.startswith("→") or stripped.startswith("-") or \
           stripped.startswith("•"):
            story.append(Paragraph(stripped, styles["body_indent"]))
            continue

        # Teaching notes / italicised hints
        if stripped.lower().startswith("teaching note:") or \
           stripped.lower().startswith("revision tip:") or \
           stripped.lower().startswith("why:") or \
           stripped.lower().startswith("answer:"):
            story.append(Paragraph(stripped, styles["note"]))
            continue

        # Default: body text
        story.append(Paragraph(stripped, styles["body"]))

    return story


def add_video_section(story, styles, video_resources):
    """Appends the Further Learning / YouTube section to the PDF."""
    story.append(PageBreak())
    story.append(Paragraph("FURTHER LEARNING", styles["section_header"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "Watch these videos to deepen your understanding of the topic.",
        styles["body"]
    ))
    story.append(Spacer(1, 0.3 * cm))

    if video_resources:
        lines = video_resources.strip().split("\n")
        for line in lines:
            stripped = line.strip()
            if not stripped:
                story.append(Spacer(1, 0.15 * cm))
            elif stripped.lower().startswith("video "):
                story.append(Paragraph(stripped, styles["subsection"]))
            elif stripped.lower().startswith("url:"):
                # Make URL visually distinct
                story.append(Paragraph(stripped, ParagraphStyle(
                    "url",
                    fontName="Courier",
                    fontSize=9,
                    textColor=TEAL,
                    spaceAfter=3,
                )))
            else:
                story.append(Paragraph(stripped, styles["body"]))
    else:
        story.append(Paragraph(
            "No video resources were found for this topic. "
            "Try searching YouTube directly for: "
            "[topic] [level] [country] explained",
            styles["note"]
        ))


def build_pdf(content_text, video_resources, output_path, doc_type,
              topic, level, country):
    """Builds a single PDF from content text and video resources."""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = build_styles()
    story = []

    # Header
    add_header_block(
        story, styles,
        title=topic.title(),
        subtitle=f"{level} · {country}",
        doc_type=doc_type,
        country=country,
        level=level,
    )

    # Generated timestamp
    story.append(Paragraph(
        f"Generated by Ujuzi Agent  ·  {datetime.now().strftime('%B %d, %Y')}",
        styles["note"]
    ))
    story.append(Spacer(1, 0.5 * cm))

    # Main content
    story.extend(parse_content_to_story(content_text, styles))

    # Video resources
    add_video_section(story, styles, video_resources)

    # Build
    doc.build(story)
    print(f"[PDF Builder] ✓ Saved: {output_path}")


def run_pdf_builder(session_state: dict, output_dir: str = "output"):
    """
    Main entry point. Called after the pipeline completes.
    Reads from session state and builds whichever PDFs are needed.
    """

    topic      = session_state.get("topic", "lesson")
    level      = session_state.get("level", "Secondary School")
    country    = session_state.get("country", "Kenya")
    plan_type  = session_state.get("plan_type", "both")
    videos     = session_state.get("video_resources", "")

    # Sanitise topic for filename
    safe_topic = topic.replace(" ", "_").replace("/", "-").lower()

    built = []

    if plan_type in ("teacher", "both"):
        teacher_content = session_state.get("teacher_content", "")
        if teacher_content:
            path = os.path.join(output_dir,
                                f"Teacher_{safe_topic}_{country}.pdf")
            build_pdf(
                content_text=teacher_content,
                video_resources=videos,
                output_path=path,
                doc_type="TEACHER LESSON PLAN",
                topic=topic,
                level=level,
                country=country,
            )
            built.append(path)
        else:
            print("[PDF Builder] ⚠ No teacher_content found in session state.")

    if plan_type in ("student", "both"):
        student_content = session_state.get("student_content", "")
        if student_content:
            path = os.path.join(output_dir,
                                f"Student_{safe_topic}_{country}.pdf")
            build_pdf(
                content_text=student_content,
                video_resources=videos,
                output_path=path,
                doc_type="STUDENT STUDY GUIDE",
                topic=topic,
                level=level,
                country=country,
            )
            built.append(path)
        else:
            print("[PDF Builder] ⚠ No student_content found in session state.")

    if built:
        print(f"\n[PDF Builder] ✓ Done. {len(built)} PDF(s) saved to /{output_dir}/")
        for p in built:
            print(f"   → {p}")
    else:
        print("[PDF Builder] ✗ No PDFs were built. Check session state.")

    return built


# ── Standalone test ────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Quick test with dummy data
    test_state = {
        "topic": "photosynthesis",
        "level": "Grade 8",
        "country": "Kenya",
        "plan_type": "both",
        "teacher_content": """LESSON PLAN
Topic: Photosynthesis
Level: Grade 8
Country: Kenya

LEARNING OBJECTIVES
By the end of this lesson, students will be able to:
1. Define photosynthesis and identify where it occurs
2. Explain the inputs and outputs of photosynthesis
3. Connect photosynthesis to food production in Kenyan farming

MATERIALS NEEDED
→ Leaves from a local plant (e.g. maize or kale from the school garden)
→ A bowl of water
→ Sunlight

LESSON OUTLINE
Introduction (5 minutes)
Ask students: Where do maize plants get their food from?
Teaching note: Expect students to say "the soil" — use this to build curiosity.

Main Teaching — Part 1 (10 minutes)
Photosynthesis is the process by which plants make their own food.
Teaching note: Draw a simple leaf on the board with arrows for sunlight, water, CO2 in and glucose, O2 out.

QUIZ — WITH ANSWER KEY
1. What gas do plants take in during photosynthesis?
Answer: Carbon dioxide (CO2)

2. A maize farmer in Kisumu notices her plants are yellowing. What might be missing?
Answer: Sunlight or water — both needed for photosynthesis.

SLIDE OUTLINE
Slide 1 — What is Photosynthesis?
Key point: Plants make their own food using sunlight.
Teaching note: Ask opening question before showing this slide.
Visual suggestion: Photo of a maize farm in the Rift Valley.

Slide 2 — The Ingredients
Key point: Plants need sunlight, water, and CO2.
Teaching note: Draw arrows on the board as you explain each input.
Visual suggestion: Simple diagram of a leaf with labelled inputs.
""",
        "student_content": """STUDY GUIDE
Topic: Photosynthesis
Level: Grade 8
Country: Kenya

WHAT YOU WILL LEARN
1. What photosynthesis is and why it matters
2. What plants need to make their food
3. How this connects to the food you eat every day

SECTION 1 — What is Photosynthesis?
Photosynthesis is how plants make their own food. Unlike you and me, plants do not need to eat — they make food inside their own leaves using sunlight, water, and air.

Did you know?
The maize on your family's farm is using photosynthesis right now to grow.

QUIZ — TEST YOURSELF
1. What gas do plants take in during photosynthesis?
2. Name two things a plant needs to carry out photosynthesis.
3. What does a plant produce during photosynthesis?
4. Why do plants need sunlight?
5. A bean plant is kept in a dark room for a week. What do you think will happen to it?

Check your answers with your teacher.
""",
        "video_resources": """VIDEO RESOURCES
───────────────

Video 1
Title:   Photosynthesis - How Plants Make Food
Channel: Cognitoedu
URL:     https://www.youtube.com/watch?v=Y2pEBzuBBo8
Why:     Clear visual explanation of the full photosynthesis process suitable for Grade 8.

Video 2
Title:   Photosynthesis for Kids
Channel: Science with Klingon
URL:     https://www.youtube.com/watch?v=CMHNBKhHkCE
Why:     Simple, engaging breakdown using plant diagrams and real examples.

Video 3
Title:   How Do Plants Make Food - Photosynthesis
Channel: Smile and Learn
URL:     https://www.youtube.com/watch?v=x1hVTy1Ys30
Why:     Animated explanation that works well for visual learners.
""",
    }

    run_pdf_builder(test_state, output_dir="output")
