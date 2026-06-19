"""Centralized application configuration loaded from environment variables."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN: str | None = os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")

ALLOWED_ORIGINS: list[str] = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

GITHUB_API_BASE = "https://api.github.com"

# Limits
MAX_REPOS = 10
BATCH_SIZE = 5
README_MAX_CHARS = 4000
AI_MAX_RETRIES = 3
AI_RETRY_DELAY_SECONDS = 3
