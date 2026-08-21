"""
UJUZI AGENT — Judge Agent (Groq)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from google.adk.agents import Agent
from pydantic import BaseModel, Field
from typing import Literal

MODEL = "groq/compound"


class JudgeFeedback(BaseModel):
    status: Literal["pass", "fail"] = Field(
        description="'pass' if all criteria met, 'fail' if any criterion fails."
    )
    feedback: str = Field(
        description="If fail: specific actionable feedback. If pass: brief confirmation."
    )
    accuracy_ok: bool = Field(description="Content is factually accurate.")
    level_ok: bool = Field(description="Content is appropriate for the specified level.")
    localisation_ok: bool = Field(description="Localisation is genuine, not superficial.")
    depth_ok: bool = Field(description="Enough content to build a complete lesson from.")


judge = Agent(
    name="judge",
    model=MODEL,
    description="Evaluates localised content for accuracy, level appropriateness, localisation quality, and depth.",
    instruction="""
You are a strict but fair educational content reviewer.

Read from session state:
    localised_findings — the Localisation Agent's output
    topic              — the subject being taught
    level              — the school grade
    country            — the country context

Evaluate against four criteria:

CRITERION 1 — FACTUAL ACCURACY
Is the content scientifically or factually correct?
→ accuracy_ok = True / False

CRITERION 2 — LEVEL APPROPRIATENESS
Is the language, depth, and complexity right for the specified level?
→ level_ok = True / False

CRITERION 3 — GENUINE LOCALISATION
Is the localisation real or superficial?
Genuine = local examples, curriculum aligned, resource-aware.
Superficial = just replaced country names.
→ localisation_ok = True / False

CRITERION 4 — SUFFICIENT DEPTH
Enough content to build a full lesson plan AND a student study guide?
→ depth_ok = True / False

Set status to "pass" ONLY if ALL FOUR criteria are True.
Set status to "fail" if ANY criterion is False.

When failing, be specific — say exactly what is missing or wrong.

Return your verdict as structured output matching the JudgeFeedback schema.
""",
    output_schema=JudgeFeedback,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)

root_agent = judge
