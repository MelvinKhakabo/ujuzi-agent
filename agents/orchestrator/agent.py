"""
UJUZI AGENT — Orchestrator
────────────────────────────
Role: The manager. Wires all specialist agents together into a
complete pipeline using ADK's SequentialAgent and LoopAgent.

Full pipeline:
──────────────
Context Agent           → extracts topic, level, country, plan_type
    │
LoopAgent (max 3)
    ├── Researcher       → finds content via web search
    ├── Localisation     → adapts to local African context
    ├── Judge            → structured pass/fail quality check
    └── EscalationChecker→ breaks loop on pass
    │
Content Builder         → builds teacher/student plans + slide outline
    │
Resource Finder         → finds YouTube videos via web search
    │
[PDF Builder runs separately as a post-processing step]

Running locally:
────────────────
All agents run on localhost. No Google Cloud. No billing.
Requires only a free Gemini API key from aistudio.google.com.
"""
from dotenv import load_dotenv
import os
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

import os
import sys
import asyncio
from typing import AsyncGenerator

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from google.adk.agents import Agent, SequentialAgent, LoopAgent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions

# ── Import all specialist agents ──────────────────────────────────────────
from agents.context_agent.agent import context_agent
from agents.researcher.agent import researcher
from agents.localisation_agent.agent import localisation_agent
from agents.judge.agent import judge
from agents.content_builder.agent import content_builder
from agents.resource_finder.agent import resource_finder

MODEL = "groq/compound-beta"


# ── Escalation Checker ────────────────────────────────────────────────────
class EscalationChecker(BaseAgent):
    """
    Checks the Judge's structured output and breaks the research loop
    if the verdict is 'pass'. If 'fail', the loop continues and the
    Researcher tries again with the Judge's feedback.

    This is pure Python logic — no LLM call needed.
    """

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:

        feedback = ctx.session.state.get("judge_feedback")
        print(f"\n[EscalationChecker] Judge feedback: {feedback}")

        is_pass = False

        # Handle structured dict output from Judge
        if isinstance(feedback, dict):
            is_pass = feedback.get("status") == "pass"

        # Handle string fallback if JSON parsing varied
        elif isinstance(feedback, str):
            is_pass = '"status": "pass"' in feedback or "'status': 'pass'" in feedback

        if is_pass:
            print("[EscalationChecker] ✓ Quality check passed — moving to content build.")
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            print("[EscalationChecker] ✗ Quality check failed — looping back to research.")
            yield Event(author=self.name)


escalation_checker = EscalationChecker(name="escalation_checker")


# ── Research + Quality Loop ───────────────────────────────────────────────
# Researcher → Localisation → Judge → EscalationChecker
# Loops up to 3 times until Judge passes or max iterations reached.

research_loop = LoopAgent(
    name="research_loop",
    description=(
        "Iteratively researches, localises, and quality-checks content "
        "until it meets the required standard or reaches 3 attempts."
    ),
    sub_agents=[
        researcher,
        localisation_agent,
        judge,
        escalation_checker,
    ],
    max_iterations=3,
)


# ── Full Pipeline ─────────────────────────────────────────────────────────
# Context → Research Loop → Content Builder → Resource Finder

root_agent = SequentialAgent(
    name="ujuzi_pipeline",
    description=(
        "A multi-agent pipeline that researches a topic, adapts it to a "
        "local African context, quality-checks it, then builds teacher "
        "lesson plans and student study guides with YouTube resources."
    ),
    sub_agents=[
        context_agent,
        research_loop,
        content_builder,
        resource_finder,
    ],
)
