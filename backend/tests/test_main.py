"""Tests for the FastAPI application."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from main import EvaluationResponse, _chunk_list, app

client = TestClient(app)


# ---------------------------------------------------------------------------
# _chunk_list tests
# ---------------------------------------------------------------------------

class TestChunkList:
    def test_empty(self) -> None:
        assert _chunk_list([], 3) == []

    def test_exact_fit(self) -> None:
        assert _chunk_list([1, 2, 3], 3) == [[1, 2, 3]]

    def test_remainder(self) -> None:
        assert _chunk_list([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]

    def test_size_one(self) -> None:
        assert _chunk_list([1, 2, 3], 1) == [[1], [2], [3]]

    def test_larger_than_list(self) -> None:
        assert _chunk_list([1], 10) == [[1]]


# ---------------------------------------------------------------------------
# API endpoint tests
# ---------------------------------------------------------------------------

class TestEvaluateEndpoint:
    def test_invalid_username_format(self) -> None:
        response = client.get("/api/evaluate/!!!invalid!!!")
        assert response.status_code == 400
        assert "Invalid" in response.json()["detail"]

    def test_empty_username(self) -> None:
        response = client.get("/api/evaluate/%20%20")
        assert response.status_code == 400

    @patch("main.get_user_repos", new_callable=AsyncMock, return_value=None)
    def test_user_not_found(self, mock_repos: AsyncMock) -> None:
        response = client.get("/api/evaluate/nonexistent-user-xyz")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @patch("main.get_user_repos", new_callable=AsyncMock, return_value=[])
    def test_user_with_no_repos(self, mock_repos: AsyncMock) -> None:
        response = client.get("/api/evaluate/empty-user")
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "empty-user"
        assert data["projects"] == []
        assert data["total_evaluated"] == 0

    @patch("main.evaluate_readmes_batch", new_callable=AsyncMock)
    @patch("main.get_readme_content", new_callable=AsyncMock)
    @patch("main.get_user_repos", new_callable=AsyncMock)
    def test_successful_evaluation(
        self,
        mock_repos: AsyncMock,
        mock_readme: AsyncMock,
        mock_ai: AsyncMock,
    ) -> None:
        mock_repos.return_value = [
            {
                "name": "my-project",
                "html_url": "https://github.com/user/my-project",
                "fork": False,
                "owner": {"login": "user"},
            },
        ]
        mock_readme.return_value = "# My Project\nA cool project."
        mock_ai.return_value = [
            {
                "repo_name": "my-project",
                "level": "Intermediate",
                "assessment": "Well-structured project.",
            }
        ]

        response = client.get("/api/evaluate/user")
        assert response.status_code == 200

        data = response.json()
        assert data["username"] == "user"
        assert data["total_evaluated"] == 1
        assert len(data["projects"]) == 1
        assert data["projects"][0]["name"] == "my-project"
        assert data["projects"][0]["evaluation"]["level"] == "Intermediate"

    @patch("main.get_readme_content", new_callable=AsyncMock, return_value=None)
    @patch("main.get_user_repos", new_callable=AsyncMock)
    def test_repo_without_readme(
        self,
        mock_repos: AsyncMock,
        mock_readme: AsyncMock,
    ) -> None:
        mock_repos.return_value = [
            {
                "name": "no-readme",
                "html_url": "https://github.com/user/no-readme",
                "fork": False,
                "owner": {"login": "user"},
            },
        ]

        response = client.get("/api/evaluate/user")
        assert response.status_code == 200

        data = response.json()
        project = data["projects"][0]
        assert project["evaluation"]["level"] == "Unknown"
        assert "No README" in project["evaluation"]["assessment"]