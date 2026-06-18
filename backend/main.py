from __future__ import annotations

import logging
import asyncio
from typing import Any, Dict, List

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from github_service import get_readme_content, get_user_repos
from ai_service import evaluate_readme

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("backend")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def _evaluate_repo(repo: Dict[str, Any]) -> Dict[str, Any]:
    repo_name = repo.get("name", "")
    owner = repo.get("owner", {}).get("login", "")
    default_branch = repo.get("default_branch", "main") or "main"

    readme_content = await get_readme_content(owner, repo_name, default_branch=default_branch)
    print(f"--- Is README found for the repo {repo_name}? {readme_content is not None} ---")
    evaluation = None
    if readme_content:
        evaluation = await evaluate_readme(repo_name, readme_content)

    return {
        "name": repo_name,
        "html_url": repo.get("html_url"),
        "evaluation": evaluation,
    }


@app.get("/api/evaluate/{username}")
async def evaluate_user_readmes(username: str) -> Dict[str, Any]:
    repos = await get_user_repos(username)
    if repos is None:
        raise HTTPException(status_code=404, detail="GitHub user not found")

    original_repos: List[Dict[str, Any]] = [
        repo for repo in repos if not repo.get("fork", False)
    ]
    selected_repos = original_repos[:10]

    projects = await asyncio.gather(*[_evaluate_repo(repo) for repo in selected_repos])
    total_evaluated = sum(1 for project in projects if project["evaluation"] is not None)

    return {
        "username": username,
        "total_evaluated": total_evaluated,
        "projects": projects,
    }


def main() -> None:
    logger.info("Starting backend server...")

    try:
        uvicorn.run(
            "main:app",
            host="127.0.0.1",
            port=8000,
            log_level="info",
            reload=False,
        )
    except Exception as exc:
        logger.exception("Server failed to start")
        raise


if __name__ == "__main__":
    main()
