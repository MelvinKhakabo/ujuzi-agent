"""
UJUZI AGENT — Groq Key Pool
─────────────────────────────
Manages multiple Groq API keys and rotates automatically
when one hits a rate limit (429) or daily quota (250 RPD).

Usage:
    from groq_pool import get_groq_client, GROQ_MODEL

    client = get_groq_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": "Hello"}]
    )
"""

import os
import time
import logging
from groq import Groq, RateLimitError, APIStatusError

logger = logging.getLogger(__name__)

# ── Model ──────────────────────────────────────────────────────────────────
GROQ_MODEL = "groq/compound"

# ── Load keys from environment ─────────────────────────────────────────────
def _load_keys():
    keys = []
    for i in range(1, 11):
        key = os.getenv(f"GROQ_API_KEY_{i}")
        if key and key.strip():
            keys.append(key.strip())
    if not keys:
        raise ValueError(
            "No Groq API keys found in environment. "
            "Add GROQ_API_KEY_1, GROQ_API_KEY_2, etc. to your .env file."
        )
    logger.info(f"[KeyPool] Loaded {len(keys)} Groq API key(s)")
    return keys

GROQ_KEYS = _load_keys()

# ── Key state tracking ─────────────────────────────────────────────────────
_key_index = 0
_key_exhausted = [False] * len(GROQ_KEYS)
_key_reset_time = [0.0] * len(GROQ_KEYS)

def _next_available_key():
    """Returns the index of the next available key, cycling through all."""
    global _key_index
    now = time.time()

    for _ in range(len(GROQ_KEYS)):
        idx = _key_index % len(GROQ_KEYS)

        # If key was rate-limited but reset time has passed, unblock it
        if _key_exhausted[idx] and now > _key_reset_time[idx]:
            _key_exhausted[idx] = False
            logger.info(f"[KeyPool] Key {idx + 1} reset — available again")

        if not _key_exhausted[idx]:
            return idx

        _key_index += 1

    # All keys exhausted — find the one with the soonest reset
    soonest = min(range(len(GROQ_KEYS)), key=lambda i: _key_reset_time[i])
    wait = max(0, _key_reset_time[soonest] - now)
    if wait > 0:
        logger.warning(f"[KeyPool] All keys exhausted. Waiting {wait:.1f}s for key {soonest + 1} to reset...")
        time.sleep(wait + 1)
        _key_exhausted[soonest] = False

    return soonest

def _mark_key_exhausted(idx, retry_after=60):
    """Mark a key as rate-limited with a reset time."""
    _key_exhausted[idx] = True
    _key_reset_time[idx] = time.time() + retry_after
    logger.warning(f"[KeyPool] Key {idx + 1} rate-limited. Rotating. Reset in {retry_after}s.")

# ── Groq client with auto-rotation ─────────────────────────────────────────
class RotatingGroqClient:
    """
    Drop-in wrapper around the Groq client that automatically
    rotates to the next available key on rate limit errors.
    """

    def __init__(self):
        self._make_client()

    def _make_client(self):
        global _key_index
        idx = _next_available_key()
        _key_index = (idx + 1) % len(GROQ_KEYS)
        self._current_idx = idx
        self._client = Groq(api_key=GROQ_KEYS[idx])
        logger.info(f"[KeyPool] Using key {idx + 1} of {len(GROQ_KEYS)}")

    def _call_with_rotation(self, fn, *args, **kwargs):
        """Execute an API call, rotating keys on rate limit errors."""
        max_attempts = len(GROQ_KEYS) * 2
        for attempt in range(max_attempts):
            try:
                return fn(*args, **kwargs)
            except RateLimitError as e:
                retry_after = 60
                try:
                    retry_after = int(e.response.headers.get("retry-after", 60))
                except Exception:
                    pass
                _mark_key_exhausted(self._current_idx, retry_after)
                self._make_client()
            except APIStatusError as e:
                if e.status_code == 429:
                    _mark_key_exhausted(self._current_idx, 60)
                    self._make_client()
                else:
                    raise
        raise RuntimeError(
            f"[KeyPool] All {len(GROQ_KEYS)} keys exhausted after {max_attempts} attempts. "
            "Add more keys or wait for quotas to reset."
        )

    @property
    def chat(self):
        return _ChatProxy(self)


class _ChatProxy:
    def __init__(self, rotating_client):
        self._rc = rotating_client

    @property
    def completions(self):
        return _CompletionsProxy(self._rc)


class _CompletionsProxy:
    def __init__(self, rotating_client):
        self._rc = rotating_client

    def create(self, **kwargs):
        return self._rc._call_with_rotation(
            self._rc._client.chat.completions.create, **kwargs
        )


# ── Public API ─────────────────────────────────────────────────────────────
_client_instance = None

def get_groq_client() -> RotatingGroqClient:
    """Returns the shared rotating Groq client."""
    global _client_instance
    if _client_instance is None:
        _client_instance = RotatingGroqClient()
    return _client_instance


def groq_chat(messages: list, max_tokens: int = 4096) -> str:
    """
    Convenience function — send messages and get the response text back.
    Handles key rotation automatically.

    Args:
        messages: List of {"role": ..., "content": ...} dicts
        max_tokens: Maximum tokens in the response

    Returns:
        The model's response as a string
    """
    client = get_groq_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.3,
    )
    return response.choices[0].message.content
