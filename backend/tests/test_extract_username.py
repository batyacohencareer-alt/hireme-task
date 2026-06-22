"""Tests for the extract_username utility."""

import pytest

from github_service import extract_username


@pytest.mark.parametrize(
    ("raw_input", "expected"),
    [
        # Plain usernames
        ("octocat", "octocat"),
        ("  octocat  ", "octocat"),
        # Full HTTPS URLs
        ("https://github.com/octocat", "octocat"),
        ("https://github.com/octocat/", "octocat"),
        ("https://www.github.com/octocat", "octocat"),
        # URL with extra path segments (repo, tree, etc.)
        ("https://github.com/octocat/hello-world", "octocat"),
        ("https://github.com/octocat/hello-world/tree/main", "octocat"),
        # URL with query params and fragments
        ("https://github.com/octocat?tab=repositories", "octocat"),
        ("https://github.com/octocat#readme", "octocat"),
        ("https://github.com/octocat?tab=repos#section", "octocat"),
        # Bare github.com path (no scheme)
        ("github.com/octocat", "octocat"),
        ("github.com/octocat/repo", "octocat"),
        # Edge cases
        ("", ""),
        ("   ", ""),
    ],
)
def test_extract_username(raw_input: str, expected: str) -> None:
    assert extract_username(raw_input) == expected


def test_extract_username_non_string() -> None:
    assert extract_username(123) == ""  # type: ignore[arg-type]
    assert extract_username(None) == ""  # type: ignore[arg-type]