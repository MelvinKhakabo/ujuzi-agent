"""
UJUZI AGENT — Judge Agent
──────────────────────────
Role: Quality gate between localisation and content building.
Returns a structured pass/fail verdict using Pydantic so the
Escalation Checker can act on it programmatically.

Evaluates the localised_findings against four criteria:
  1. Factual accuracy
  2. Age/level appropriateness
  3. Genuine localisation (not just surface changes)
  4. Sufficient depth to build a full lesson from

Reads:  localised_findings, topic, level, country from session state
Output: Structured JudgeFeedback (pass/fail + specific feedback)
"""

from google.adk.agents import Agent
from pydantic import BaseModel, Field
from typing import Literal

MODEL = "gemini-2.0-flash-lite"


class JudgeFeedback(BaseModel):
    """Structured verdict from the Judge agent."""

    status: Literal["pass", "fail"] = Field(
        description=(
            "'pass' if the localised content meets all four quality criteria. "
            "'fail' if any criterion is not met."
        )
    )
    feedback: str = Field(
        description=(
            "If 'fail': specific, actionable feedback on exactly what is "
            "missing or wrong so the Researcher can improve it. "
            "If 'pass': a brief confirmation of what was done well."
        )
    )
    accuracy_ok: bool = Field(
        description="True if the content is factually accurate."
    )
    level_ok: bool = Field(
        description="True if the content is appropriate for the specified level."
    )
    localisation_ok: bool = Field(
        description=(
            "True if localisation is genuine — local examples, "
            "curriculum alignment, resource awareness."
        )
    )
    depth_ok: bool = Field(
        description=(
            "True if there is enough content to build a complete lesson plan "
            "and study guide from."
        )
    )


judge = Agent(
    name="judge",
    model=MODEL,
    description=(
        "Evaluates localised lesson content for accuracy, appropriateness, "
        "genuine localisation, and sufficient depth."
    ),
    instruction="""
    You are a strict but fair educational content reviewer.

    Read the following from session state:
        localised_findings  — the Localisation Agent's output
        topic               — the subject being taught
        level               — the school grade/year
        country             — the country context

    Evaluate the localised_findings against these four criteria:

    ─────────────────────────────────────────────────────────────────
    CRITERION 1 — FACTUAL ACCURACY
    Is the content scientifically or factually correct?
    Are definitions precise? Are processes described correctly?
    → accuracy_ok = True / False

    CRITERION 2 — LEVEL APPROPRIATENESS
    Is the language, depth, and complexity right for the specified level?
    Would a student at this level understand it without a university degree?
    Would a teacher at this level find it useful and not patronising?
    → level_ok = True / False

    CRITERION 3 — GENUINE LOCALISATION
    Is the localisation real or superficial?
    → Superficial: just replaced country names but kept foreign examples
    → Genuine: examples, activities, units, curriculum aligned to country
    → level_ok = True / False

    CRITERION 4 — SUFFICIENT DEPTH
    Is there enough content to build:
      - A full teacher lesson plan with objectives and activities?
      - A student study guide with explanations and a quiz?
    → depth_ok = True / False
    ─────────────────────────────────────────────────────────────────

    Set status to "pass" ONLY if ALL FOUR criteria are True.
    Set status to "fail" if ANY criterion is False.

    When failing, your feedback must be specific:
    → Do not say "needs more detail". Say exactly what is missing.
    → Do not say "localisation is weak". Say exactly what was not localised.

    Return your verdict as structured output matching the JudgeFeedback schema.
    """,
    output_schema=JudgeFeedback,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)

root_agent = judge
