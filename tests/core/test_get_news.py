"""
test_get_news.py
Tests for get_news core function.
"""
from datetime import datetime, timezone, timedelta
from digest.core import get_news

import pytest


DATES = (
    datetime(2026, 7, 17, tzinfo=timezone.utc),
    datetime(2026, 7, 24, tzinfo=timezone.utc)
)


def test_get_news_valid_article_date_included(mocker, make_entry, make_feed):
    entry = make_entry(published_parsed=(2026, 7, 20, 10, 0, 0, 0, 0, 0))

    mocker.patch("digest.core.feedparser.parse", return_value=make_feed([entry]))

    news = get_news(DATES, [{"title": "Feed Name", "url": "http://example.com/feed"}], silent=True)
    assert len(news) == 1
    assert news[0]["title"] == "Article"
    assert news[0]["link"] == "http://example.com/article"
    assert news[0]["category"] == "Feed Name"


def test_get_news_invalid_article_date_excluded(mocker, make_entry, make_feed):
    entry = make_entry(published_parsed=(2026, 7, 1, 10, 0, 0, 0, 0, 0))

    mocker.patch("digest.core.feedparser.parse", return_value=make_feed([entry]))

    news = get_news(DATES, [{"title": "Feed Name", "url": "http://example.com/feed"}], silent=True)
    assert news == []


def test_get_news_missing_article_date_excluded(mocker, make_entry, make_feed):
    entry = make_entry()
    entry.published_parsed = None

    mocker.patch("digest.core.feedparser.parse", return_value=make_feed([entry]))

    news = get_news(DATES, [{"title": "Feed Name", "url": "http://example.com/feed"}], silent=True)
    assert news == []


def test_get_news_duplicate_article_excluded(mocker, make_entry, make_feed):
    entry_a = make_entry(link="http://example.com/article", published_parsed=(2026, 7, 20, 10, 0, 0, 0, 0, 0))
    entry_b = make_entry(link="http://example.com/article", published_parsed=(2026, 7, 21, 10, 0, 0, 0, 0, 0))

    mocker.patch("digest.core.feedparser.parse", return_value=make_feed([entry_a, entry_b]))

    news = get_news(DATES, [{"title": "Feed Name", "url": "http://example.com/feed"}], silent=True)
    assert len(news) == 1
