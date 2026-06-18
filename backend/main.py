from __future__ import annotations

import logging
import asyncio
from typing import Any, Dict, List

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from github_service import get_readme_content, get_user_repos
from ai_service import evaluate_readmes_batch

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


def _chunk_list(items: List[Any], size: int = 5) -> List[List[Any]]:
	return [items[i : i + size] for i in range(0, len(items), size)]


async def _fetch_readmes(repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
	async def _fetch(repo: Dict[str, Any]) -> Dict[str, Any]:
		repo_name = repo.get("name", "")
		owner = repo.get("owner", {}).get("login", "")
		default_branch = repo.get("default_branch", "main") or "main"

		readme_content = await get_readme_content(owner, repo_name, default_branch=default_branch)
		print(f"--- Is README found for the repo {repo_name}? {readme_content is not None} ---")
		return {"repo": repo, "readme_content": readme_content}

	return await asyncio.gather(*[_fetch(repo) for repo in repos])


@app.get("/api/evaluate/{username}")
async def evaluate_user_readmes(username: str) -> Dict[str, Any]:
	repos = await get_user_repos(username)
	if repos is None:
		raise HTTPException(status_code=404, detail="GitHub user not found")

	if not isinstance(repos, list):
		raise HTTPException(status_code=400, detail="Unexpected GitHub response format")

	original_repos: List[Dict[str, Any]] = [
		repo for repo in repos if not repo.get("fork", False)
	]
	selected_repos = original_repos[:10]

	repo_entries = await _fetch_readmes(selected_repos)
	readme_entries = [entry for entry in repo_entries if entry["readme_content"]]

	evaluations: List[Dict[str, Any]] = []
	for batch in _chunk_list(readme_entries, 5):
		batch_payload = [
			{"repo_name": entry["repo"].get("name", ""), "readme_content": entry["readme_content"]}
			for entry in batch
		]
		evaluations.extend(await evaluate_readmes_batch(batch_payload))

	evaluation_map = {
		item.get("repo_name", ""): item for item in evaluations if item.get("repo_name")
	}

	projects = []
	for entry in repo_entries:
		repo = entry["repo"]
		repo_name = repo.get("name", "")
		if not entry["readme_content"]:
			evaluation = {"level": "Unknown", "assessment": "No README found."}
		else:
			evaluation = evaluation_map.get(
				repo_name,
				{"level": "Error", "assessment": "AI processing failed."},
			)

		projects.append(
			{
				"name": repo_name,
				"html_url": repo.get("html_url"),
				"evaluation": evaluation,
			}
		)

	total_evaluated = sum(
		1
		for project in projects
		if project["evaluation"] is not None and project["evaluation"].get("level") != "Unknown"
	)

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
