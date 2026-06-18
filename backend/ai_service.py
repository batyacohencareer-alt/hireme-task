import logging
import os
import json
import asyncio
from typing import Any, Dict, List

from google import genai
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

try:
    load_dotenv()
    logger.info("Loaded .env in ai_service")
except Exception:
    logger.exception("Failed to load .env in ai_service")

# אתחול הלקוח עם מפתח ה-API
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


async def evaluate_readmes_batch(repos: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    if not repos:
        return []

    prompt_parts = [
        "Please evaluate the following repository READMEs and return ONLY a valid JSON array.",
        "Do not include markdown formatting, code fences, or any text outside the JSON array.",
        "Each object must look exactly like: {\"repo_name\": \"name\", \"level\": \"Beginner/Advanced/etc\", \"assessment\": \"short string\"}.",
    ]

    for repo in repos:
        repo_name = repo.get("repo_name", "")
        content = repo.get("readme_content", "")
        prompt_parts.append(f"--- START REPO: {repo_name} ---")
        prompt_parts.append(content)
        prompt_parts.append(f"--- END REPO: {repo_name} ---")

    prompt = "\n".join(prompt_parts)
    max_retries = 3

    def _strip_markdown_json(raw_text: str) -> str:
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned.removeprefix("```json")
        elif cleaned.startswith("```"):
            cleaned = cleaned.removeprefix("```")

        if cleaned.endswith("```"):
            cleaned = cleaned.removesuffix("```")

        return cleaned.strip()

    for attempt in range(1, max_retries + 1):
        try:
            print(f"--- PROMPT ---:\n{prompt}\n--- END PROMPT ---")
            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )

            # ניקוי המחרוזת והפיכה ל-JSON
            text = _strip_markdown_json(response.text)
            parsed = json.loads(text)
            if not isinstance(parsed, list):
                raise ValueError("Expected a JSON array from Gemini.")

            return parsed

        except Exception as e:
            err_text = str(e)
            print(f"--- AI ERROR (attempt {attempt}) ---: {e}")

            is_rate_limit = False
            lower = err_text.lower()
            if "429" in err_text or "resource_exhausted" in lower or "rate limit" in lower:
                is_rate_limit = True

            if is_rate_limit and attempt < max_retries:
                await asyncio.sleep(3)
                continue

            return [
                {
                    "repo_name": repo.get("repo_name", ""),
                    "level": "Error",
                    "assessment": "AI processing failed.",
                }
                for repo in repos
            ]
