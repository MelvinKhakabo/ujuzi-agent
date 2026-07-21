"""
UJUZI AGENT — Context Agent
────────────────────────────
Role: Entry point of the pipeline. Reads the user's free-text prompt and
extracts four structured pieces of information that every downstream agent
will read from session state:

    topic       — the subject to teach  (e.g. "photosynthesis")
    level       — the school grade/year (e.g. "Grade 8")
    country     — the local context     (e.g. "Kenya")
    plan_type   — what to generate      ("teacher", "student", or "both")

No web search. No content generation. Just structured understanding.
"""

from google.adk.agents import Agent

MODEL = "gemini-2.0-flash"

context_agent = Agent(
    name="context_agent",
    model=MODEL,
    description=(
        "Reads the user's request and extracts the topic, education level, "
        "country, and plan type needed to generate the lesson."
    ),
    instruction="""
    You are the first agent in a lesson-generation pipeline.

    Your ONLY job is to read the user's request and extract exactly four pieces
    of information. Save them to session state using the keys below.

    Keys to extract and save:
    ─────────────────────────
    topic        The subject or concept to be taught.
                 Example: "photosynthesis", "the water cycle", "fractions"

    level        The school grade or education level.
                 Example: "Grade 8", "Form 3", "Primary 6", "Secondary School"
                 If not specified, default to "Secondary School".

    country      The country whose curriculum and context should be used.
                 Example: "Kenya", "Ghana", "Uganda", "Nigeria"
                 If not specified, default to "Kenya".

    plan_type    What type of plan to generate.
                 Must be exactly one of: "teacher", "student", or "both"
                 If the user says "lesson plan" or "teacher" → use "teacher"
                 If the user says "study guide" or "student" → use "student"
                 If not specified, default to "both".

    ─────────────────────────
    After saving these four values to session state, confirm back to the user
    in a single short sentence what you understood. For example:

    "Got it — generating a teacher lesson plan on photosynthesis for
    Grade 8 students in Kenya."

    Do not do any research. Do not generate any content. Just extract,
    save, and confirm.
    """,
)

root_agent = context_agent
