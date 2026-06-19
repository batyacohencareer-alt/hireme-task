"""Service for interacting with the GitHub API."""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlparse

import httpx

from config import GITHUB_API_BASE, GITHUB_TOKEN

logger = logging.getLogger(__name__)

_REQUEST_TIMEOUT = 15.0


def extract_username(input_string: str) -> str:
    """Extract a GitHub username from a raw string (URL or plain username).

    Handles full GitHub profile URLs, bare usernames, and URLs with
    extra path segments, query params, or fragments.
    """
    if not isinstance(input_string, str):
        return ""

    cleaned = input_string.strip()
    if not cleaned:
        return ""

    # Strip query parameters and fragments
    if "?" in cleaned:
        cleaned = cleaned.split("?", 1)[0]
    if "#" in cleaned:
        cleaned = cleaned.split("#", 1)[0]

    parsed = urlparse(cleaned)
    path = parsed.path if parsed.scheme and parsed.netloc else cleaned
    path = path.strip("/")

    if path.lower().startswith("github.com/"):
        path = path.split("/", 1)[1]

    # Isolate first path segment (the username)
    if "/" in path:
        path = path.split("/", 1)[0]

    return path


def _build_headers(accept: str = "application/vnd.github+json") -> dict[str, str]:
    """Build common headers for GitHub API requests."""
    headers: dict[str, str] = {
        "Accept": accept,
        "User-Agent": "github-evaluator",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"******"
    return headers


async def get_user_repos(username: str) -> list[dict[str, Any]] | None:
    """Fetch public, non-fork repositories for a GitHub user.

    Returns ``None`` when the user is not found or the request fails.
    """
    username = extract_username(username)
    if not username:
        return None

    url = f"{GITHUB_API_BASE}/users/{username}/repos"
    params = {"per_page": 100, "sort": "updated", "type": "owner"}

    async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT, headers=_build_headers()) as client:
        try:
            response = await client.get(url, params=params)

            if response.status_code == 404:
                return None

            response.raise_for_status()
            data = response.json()

            if not isinstance(data, list):
                return None

            return data
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            logger.warning("Failed to fetch repos for %s: %s", username, exc)
            return None


async def get_readme_content(owner: str, repo: str) -> str | None:
    """Fetch raw README content via the GitHub Contents API.

    Uses the ``/repos/{owner}/{repo}/readme`` endpoint which automatically
    resolves README files regardless of filename casing or branch.
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/readme"
    headers = _build_headers(accept="application/vnd.github.v3.raw")

    async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT, headers=headers) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
        except (httpx.HTTPStatusError, httpx.RequestError):
            return None
