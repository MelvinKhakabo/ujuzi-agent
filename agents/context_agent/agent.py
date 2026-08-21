"""
UJUZI AGENT — Context Agent (Groq)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from google.adk.agents import Agent

MODEL = "gemini-3.6-flash"

context_agent = Agent(
    name="context_agent",
    model=MODEL,
    description="Reads the user's request and extracts topic, level, country, and plan type.",
    instruction="""
You are the first agent in a lesson-generation pipeline.

Read the user's request and extract exactly four pieces of information.
Save them to session state using these exact keys:

topic       — the subject to teach (e.g. "photosynthesis")
level       — the school grade (e.g. "Grade 8"). Default: "Secondary School"
country     — the country context (e.g. "Kenya"). Default: "Kenya"
plan_type   — one of: "teacher", "student", or "both". Default: "both"

After saving, confirm in one short sentence.
Example: "Got it — generating a teacher lesson plan on photosynthesis for Grade 8 students in Kenya."

Do not research or generate any content. Extract and confirm only.
""",
)

root_agent = context_agent
