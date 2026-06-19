"""Service for evaluating repository READMEs using Google Gemini."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from google import genai

from config import (
    AI_MAX_RETRIES,
    AI_RETRY_DELAY_SECONDS,
    GEMINI_API_KEY,
    README_MAX_CHARS,
)

logger = logging.getLogger(__name__)

# Lazily initialized Gemini client — validated at app startup, not at import.
_client: genai.Client | None = None


def _get_client() -> genai.Client:
    """Return the Gemini client, creating it on first call."""
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. "
                "Add it to your .env file (see .env.example)."
            )
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def _strip_markdown_json(raw_text: str) -> str:
    """Remove markdown code-fence wrappers from a JSON string."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned.removeprefix("```json")
    elif cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```")
    if cleaned.endswith("```"):
        cleaned = cleaned.removesuffix("```")
    return cleaned.strip()


def _truncate(text: str, max_chars: int = README_MAX_CHARS) -> str:
    """Truncate text to a maximum character count."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n[...truncated]"


def _is_retryable(error_text: str) -> bool:
    """Determine whether an error is retryable (rate-limit or transient)."""
    lower = error_text.lower()
    return (
        "429" in error_text
        or "resource_exhausted" in lower
        or "rate limit" in lower
    )


async def evaluate_readmes_batch(
    repos: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """Send a batch of READMEs to Gemini for evaluation.

    Each README is truncated to prevent context-window overflow.
    Retries on both rate-limit errors and malformed JSON responses.
    """
    if not repos:
        return []

    prompt_parts = [
        "You are a senior software engineer evaluating repository READMEs.",
        "Return ONLY a valid JSON array — no markdown, no code fences, no extra text.",
        'Each object: {"repo_name": "<name>", "level": "Beginner|Intermediate|Advanced", "assessment": "<1-2 sentence evaluation>"}.',
        "",
    ]

    for repo in repos:
        repo_name = repo.get("repo_name", "")
        content = _truncate(repo.get("readme_content", ""))
        prompt_parts.append(f"--- START REPO: {repo_name} ---")
        prompt_parts.append(content)
        prompt_parts.append(f"--- END REPO: {repo_name} ---")
        prompt_parts.append("")

    prompt = "\n".join(prompt_parts)
    client = _get_client()

    for attempt in range(1, AI_MAX_RETRIES + 1):
        try:
            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )

            text = _strip_markdown_json(response.text)
            parsed = json.loads(text)

            if not isinstance(parsed, list):
                raise ValueError("Expected a JSON array from Gemini.")

            return parsed

        except (json.JSONDecodeError, ValueError) as exc:
            logger.warning(
                "JSON parse error on attempt %d/%d: %s",
                attempt, AI_MAX_RETRIES, exc,
            )
            if attempt < AI_MAX_RETRIES:
                await asyncio.sleep(AI_RETRY_DELAY_SECONDS)
                continue

        except Exception as exc:
            err_text = str(exc)
            logger.warning(
                "AI error on attempt %d/%d: %s",
                attempt, AI_MAX_RETRIES, err_text,
            )

            if _is_retryable(err_text) and attempt < AI_MAX_RETRIES:
                await asyncio.sleep(AI_RETRY_DELAY_SECONDS)
                continue

    # All retries exhausted — return error placeholders
    return [
        {
            "repo_name": repo.get("repo_name", ""),
            "level": "Error",
            "assessment": "AI processing failed.",
        }
        for repo in repos
    ]
