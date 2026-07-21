#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# UJUZI AGENT — Local Runner
# ─────────────────────────────────────────────────────────────────────────────
# Starts the full multi-agent pipeline locally.
# No Google Cloud. No billing. Just a free Gemini API key.
#
# BEFORE RUNNING:
#   1. Copy .env.template to .env and add your API key
#   2. Run: pip install -r requirements.txt
#   3. Run: chmod +x run_local.sh
#   4. Run: ./run_local.sh
# ─────────────────────────────────────────────────────────────────────────────

set -e  # Exit on any error

# ── Load environment variables ────────────────────────────────────────────
if [ ! -f .env ]; then
    echo ""
    echo "  ✗ ERROR: .env file not found."
    echo ""
    echo "  To fix this:"
    echo "  1. Copy the template:  cp .env.template .env"
    echo "  2. Open .env and paste your Gemini API key"
    echo "  3. Get a free key at:  https://aistudio.google.com"
    echo ""
    exit 1
fi

source .env

if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your_api_key_here" ]; then
    echo ""
    echo "  ✗ ERROR: GOOGLE_API_KEY is not set in your .env file."
    echo ""
    echo "  To fix this:"
    echo "  1. Go to https://aistudio.google.com"
    echo "  2. Click 'Get API Key' → 'Create API key'"
    echo "  3. Paste the key into your .env file"
    echo ""
    exit 1
fi

# ── Create output directory ───────────────────────────────────────────────
mkdir -p output

# ── Print startup message ─────────────────────────────────────────────────
echo ""
echo "  ╔═══════════════════════════════════════════════╗"
echo "  ║           UJUZI AGENT — Starting up           ║"
echo "  ╚═══════════════════════════════════════════════╝"
echo ""
echo "  API key:  found ✓"
echo "  Output:   ./output/"
echo ""
echo "  Opening the agent interface in your browser..."
echo "  If it does not open automatically, go to:"
echo "  → http://localhost:8000"
echo ""
echo "  Example prompt to try:"
echo "  'Create a lesson on photosynthesis for Grade 8"
echo "   students in Kenya. Generate both plans.'"
echo ""
echo "  Press Ctrl+C to stop the agent."
echo ""

# ── Start the ADK web interface ───────────────────────────────────────────
adk web agents/orchestrator
