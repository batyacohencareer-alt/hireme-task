"""FastAPI application for evaluating GitHub user READMEs with AI."""

from __future__ import annotations

import asyncio
import logging
import re

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ai_service import evaluate_readmes_batch
from config import ALLOWED_ORIGINS, BATCH_SIZE, MAX_REPOS
from github_service import get_readme_content, get_user_repos

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s",
)
logger = logging.getLogger("backend")

# ---------------------------------------------------------------------------
# Pydantic response models
# ---------------------------------------------------------------------------

class Evaluation(BaseModel):
    level: str
    assessment: str


class ProjectResult(BaseModel):
    name: str
    html_url: str | None = None
    evaluation: Evaluation


class EvaluationResponse(BaseModel):
    username: str
    total_evaluated: int
    projects: list[ProjectResult]


# ---------------------------------------------------------------------------
# Application setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="GitHub AI Evaluator",
    description="Analyze GitHub repositories using AI-powered README evaluation.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_USERNAME_RE = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,37}[a-zA-Z0-9])?$")


def _validate_username(username: str) -> str:
    """Validate that *username* looks like a legal GitHub login."""
    username = username.strip()
    if not _USERNAME_RE.match(username):
        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub username format.",
        )
    return username


def _chunk_list[T](items: list[T], size: int = BATCH_SIZE) -> list[list[T]]:
    """Split *items* into sublists of at most *size* elements."""
    return [items[i : i + size] for i in range(0, len(items), size)]


async def _fetch_readmes(
    repos: list[dict],
) -> list[dict]:
    """Concurrently fetch README content for each repository."""

    async def _fetch(repo: dict) -> dict:
        repo_name: str = repo.get("name", "")
        owner: str = repo.get("owner", {}).get("login", "")
        readme_content = await get_readme_content(owner, repo_name)
        return {"repo": repo, "readme_content": readme_content}

    return list(await asyncio.gather(*[_fetch(r) for r in repos]))


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get(
    "/api/evaluate/{username}",
    response_model=EvaluationResponse,
    summary="Evaluate a GitHub user's repositories",
)
async def evaluate_user_readmes(username: str) -> EvaluationResponse:
    """Fetch a user's repos, read their READMEs, and evaluate them with AI."""
    username = _validate_username(username)

    repos = await get_user_repos(username)
    if repos is None:
        raise HTTPException(status_code=404, detail="GitHub user not found")

    # Filter to original (non-fork) repos and cap
    original_repos = [r for r in repos if not r.get("fork", False)]
    selected_repos = original_repos[:MAX_REPOS]

    repo_entries = await _fetch_readmes(selected_repos)
    readme_entries = [e for e in repo_entries if e["readme_content"]]

    # Evaluate in batches
    evaluations: list[dict] = []
    for batch in _chunk_list(readme_entries, BATCH_SIZE):
        batch_payload = [
            {
                "repo_name": entry["repo"].get("name", ""),
                "readme_content": entry["readme_content"],
            }
            for entry in batch
        ]
        evaluations.extend(await evaluate_readmes_batch(batch_payload))

    evaluation_map = {
        item.get("repo_name", ""): item
        for item in evaluations
        if item.get("repo_name")
    }

    # Build response
    projects: list[ProjectResult] = []
    for entry in repo_entries:
        repo = entry["repo"]
        repo_name = repo.get("name", "")

        if not entry["readme_content"]:
            evaluation = Evaluation(level="Unknown", assessment="No README found.")
        else:
            raw = evaluation_map.get(repo_name)
            if raw:
                evaluation = Evaluation(
                    level=raw.get("level", "Error"),
                    assessment=raw.get("assessment", "AI processing failed."),
                )
            else:
                evaluation = Evaluation(
                    level="Error",
                    assessment="AI processing failed.",
                )

        projects.append(
            ProjectResult(
                name=repo_name,
                html_url=repo.get("html_url"),
                evaluation=evaluation,
            )
        )

    total_evaluated = sum(
        1 for p in projects if p.evaluation.level not in ("Unknown", "Error")
    )

    return EvaluationResponse(
        username=username,
        total_evaluated=total_evaluated,
        projects=projects,
    )


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    logger.info("Starting backend server...")
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        log_level="info",
        reload=False,
    )


if __name__ == "__main__":
    main()
