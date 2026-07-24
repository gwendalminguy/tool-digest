"""
conftest.py
Tests configuration and fixtures.
"""
from unittest.mock import Mock

import pytest


@pytest.fixture
def tmp_news_dir(tmp_path):
    """
    Temporary news/ directory for markdown files.
    """
    news_dir = tmp_path / "news"
    news_dir.mkdir()

    return news_dir


@pytest.fixture
def make_entry():
    def _make(
        title="Article",
        link="http://example.com/article",
        summary="<p>Content</p>",
        published_parsed=(2026, 7, 20, 10, 0, 0, 0, 0, 0)
    ):
        """
        Create an article.
        """
        entry = Mock(spec=["title", "link", "summary", "published_parsed"])

        entry.title = title
        entry.link = link
        entry.summary = summary
        entry.published_parsed = published_parsed

        return entry
    return _make


@pytest.fixture
def make_feed():
    def _make(entries, bozo=False, bozo_exception=None):
        """
        Create a feed.
        """
        feed = Mock()

        feed.bozo = bozo
        feed.bozo_exception = bozo_exception
        feed.entries = entries

        return feed
    return _make
