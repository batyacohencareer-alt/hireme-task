"""Tests for the AI service module."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_service import _strip_markdown_json, _truncate, evaluate_readmes_batch


class TestStripMarkdownJson:
    def test_plain_json(self) -> None:
        assert _strip_markdown_json('[{"a": 1}]') == '[{"a": 1}]'

    def test_json_code_fence(self) -> None:
        assert _strip_markdown_json('```json\n[{"a": 1}]\n```') == '[{"a": 1}]'

    def test_generic_code_fence(self) -> None:
        assert _strip_markdown_json('```\n[{"a": 1}]\n```') == '[{"a": 1}]'

    def test_whitespace(self) -> None:
        assert _strip_markdown_json('  [{"a": 1}]  ') == '[{"a": 1}]'


class TestTruncate:
    def test_short_text_unchanged(self) -> None:
        assert _truncate("hello", 100) == "hello"

    def test_long_text_truncated(self) -> None:
        result = _truncate("a" * 200, 50)
        assert len(result) < 200
        assert result.endswith("[...truncated]")


class TestEvaluateReadmesBatch:
    def test_empty_input(self) -> None:
        import asyncio
        result = asyncio.run(evaluate_readmes_batch([]))
        assert result == []

    @patch("ai_service._get_client")
    def test_successful_response(self, mock_get_client: MagicMock) -> None:
        import asyncio

        mock_response = MagicMock()
        mock_response.text = '[{"repo_name": "test", "level": "Advanced", "assessment": "Great"}]'

        mock_client = MagicMock()
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        repos = [{"repo_name": "test", "readme_content": "# Test"}]
        result = asyncio.run(evaluate_readmes_batch(repos))

        assert len(result) == 1
        assert result[0]["repo_name"] == "test"
        assert result[0]["level"] == "Advanced"

    @patch("ai_service._get_client")
    def test_all_retries_exhausted(self, mock_get_client: MagicMock) -> None:
        import asyncio

        mock_client = MagicMock()
        mock_client.aio.models.generate_content = AsyncMock(
            side_effect=Exception("connection error"),
        )
        mock_get_client.return_value = mock_client

        repos = [{"repo_name": "fail", "readme_content": "# Fail"}]
        result = asyncio.run(evaluate_readmes_batch(repos))

        assert len(result) == 1
        assert result[0]["level"] == "Error"