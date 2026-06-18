from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import httpx
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

try:
    load_dotenv()
    logger.info("Loaded .env in github_service")
except Exception:
    logger.exception("Failed to load .env in github_service")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API_BASE = "https://api.github.com"
RAW_GITHUB_BASE = "https://raw.githubusercontent.com"


def _build_headers() -> Dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-service-client",
    }

    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    return headers


async def get_user_repos(username: str) -> Optional[Any]:
    """Fetch public repositories for a GitHub user."""
    url = f"{GITHUB_API_BASE}/users/{username}/repos"

    async with httpx.AsyncClient(timeout=10.0, headers=_build_headers()) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPStatusError, httpx.RequestError):
            return None


async def get_readme_content(
    owner: str,
    repo: str,
    default_branch: str = "main",
) -> Optional[str]:
    """Fetch raw README.md content from a repository, falling back to master."""
    branches = [default_branch, "master"]
    headers = {
        "Accept": "application/vnd.github.v3.raw",
        "User-Agent": "github-service-client",
    }

    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
        for branch in branches:
            url = f"{RAW_GITHUB_BASE}/{owner}/{repo}/{branch}/README.md"
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.text
            except (httpx.HTTPStatusError, httpx.RequestError):
                continue

    return None
