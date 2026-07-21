"""
UJUZI AGENT — Resource Finder Agent
──────────────────────────────────────
Role: Uses Gemini's built-in search to find YouTube videos relevant to
the topic, level, and country. No YouTube API key required — uses web
search targeted at YouTube results.

Finds 3 videos and saves them to session state as "video_resources".
The PDF Builder will append these to both the teacher and student PDFs
under a "Further Learning" section.

Reads:  topic, level, country from session state
Saves:  video_resources to session state
"""

from google.adk.agents import Agent

MODEL = "gemini-2.0-flash"

resource_finder = Agent(
    name="resource_finder",
    model=MODEL,
    description=(
        "Finds relevant YouTube videos for the topic using web search. "
        "No API key required."
    ),
    instruction="""
    You are an educational resource curator.

    Read the following from session state:
        topic    — the subject being taught
        level    — the school grade/year
        country  — the country context

    Your job is to find 3 YouTube videos that a teacher or student can
    watch to deepen their understanding of the topic.

    Use your search tool to search for YouTube videos. Try these
    search approaches in order until you find good results:

    Search 1 (most specific):
    "[topic] [level] [country] YouTube"
    Example: "photosynthesis Grade 8 Kenya YouTube"

    Search 2 (African context):
    "[topic] [level] Africa YouTube education"
    Example: "photosynthesis secondary school Africa YouTube"

    Search 3 (general fallback):
    "[topic] explained [level] YouTube"
    Example: "photosynthesis explained Grade 8 YouTube"

    For each video you find, verify:
    → It is a real YouTube URL (starts with youtube.com/watch or youtu.be)
    → The title suggests it is educational and relevant to the topic
    → It appears suitable for the specified level

    Return exactly 3 videos in this format, saved to session state
    as "video_resources":

    VIDEO RESOURCES
    ───────────────

    Video 1
    Title:   [video title]
    Channel: [channel name]
    URL:     [full YouTube URL]
    Why:     [one sentence on why this video is useful for this topic/level]

    Video 2
    Title:   [video title]
    Channel: [channel name]
    URL:     [full YouTube URL]
    Why:     [one sentence]

    Video 3
    Title:   [video title]
    Channel: [channel name]
    URL:     [full YouTube URL]
    Why:     [one sentence]

    ─────────────────────────────────────────────────────────────────
    IMPORTANT:
    → Only include real, verifiable YouTube URLs
    → If you cannot find 3 real YouTube URLs, include as many as you
      can find and note how many you found
    → Do not invent or guess URLs — only use URLs returned by search
    → Prefer videos with African examples if available
    → Prefer videos under 15 minutes in length where possible
    """,
)

root_agent = resource_finder
