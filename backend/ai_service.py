import logging
import os
import json
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


async def evaluate_readme(repo_name: str, readme_content: str):
    if not readme_content:
        return {"level": "Unknown", "assessment": "No README found."}

    prompt = f"""
    Evaluate this README for {repo_name}. 
    Return ONLY JSON with keys: "level", "assessment".
    README: {readme_content[:5000]}
    """

    try:
        print(f"--- PROMPT ---:\n{prompt}\n--- END PROMPT ---")
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        # ניקוי המחרוזת והפיכה ל-JSON
        text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(text)

    except Exception as e:
        print(f"--- AI ERROR ---: {e}")

        return {"level": "Error", "assessment": "AI processing failed."}
