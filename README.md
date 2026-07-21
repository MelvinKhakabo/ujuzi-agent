# Ujuzi Agent

A multi-agent AI system that researches, localises, and builds teacher lesson plans and student study guides — designed for African classroom contexts.

Built with [Google ADK](https://google.github.io/adk-docs/) and the free Gemini API (no Google Cloud billing required).

---

## What it does

Given a topic, school level, and country, Ujuzi Agent:

1. **Researches** the topic using web search
2. **Localises** the content — adapts examples, curriculum alignment, and resource assumptions to the specified African country
3. **Quality-checks** the content in a feedback loop
4. **Builds** a teacher lesson plan and/or student study guide with quizzes and a slide outline
5. **Finds** YouTube videos on the topic
6. **Generates PDFs** for both teacher and student

---

## Agent architecture

```
Context Agent          → extracts topic, level, country, plan type
    │
Research Loop (max 3 iterations)
    ├── Researcher       → finds content via web search
    ├── Localisation     → adapts to local African context
    ├── Judge            → structured pass/fail quality check
    └── Escalation Checker → breaks loop on pass
    │
Content Builder        → builds lesson plans + slide outline + quizzes
    │
Resource Finder        → finds YouTube videos via web search
    │
PDF Builder            → assembles and saves PDFs to /output
```

---

## Quickstart

### 1. Clone the repo

```bash
git clone https://github.com/MelvinKhakabo/ujuzi-agent.git
cd ujuzi-agent
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up your API key

```bash
cp .env.template .env
```

Open `.env` and paste your free Gemini API key.
Get one at → [https://aistudio.google.com](https://aistudio.google.com) (no billing required)

### 4. Run

```bash
chmod +x run_local.sh
./run_local.sh
```

Open your browser at `http://localhost:8000`

---

## Example prompt

```
Create a lesson on the water cycle for Grade 6 students in Ghana.
Generate both the teacher and student plans.
```

---

## Output

PDFs are saved to the `/output` folder:

- `Teacher_[topic]_[country].pdf` — lesson plan, quiz with answers, slide outline
- `Student_[topic]_[country].pdf` — study guide, quiz without answers, slide outline

---

## Requirements

- Python 3.10+
- A free Google account (for the Gemini API key)
- No Google Cloud account needed
- No billing required

---

## Built for

[Dream Big Conference 2026](https://wellsmountain.org) — Wells Mountain Initiative, USIU-A Nairobi
Workshop: *AI Across Industries: Education, Healthcare & Business*
Facilitator: Melvin Khakabo, Learning Sprouts
