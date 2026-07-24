"""
test_get_feeds.py
Tests for get_feeds core function.
"""
from digest.core import get_feeds

import pytest
import requests


VALID_OPML = b"<opml><body><outline text='Test' title='Test'><outline text='A' xmlUrl='http://a'/><outline title='B' xmlUrl='http://b'/></outline></body></opml>"
INVALID_OPML = b"<opml><body><outline text='Test' title='Test'><outline text='A' xmlUrl='http://a'/><outline title='B' xmlUrl='http://b'/></opml>"
EMPTY_OPML = b"<opml><body></body></opml>"


def test_get_feeds_success(mocker):
    mock_response = mocker.Mock()
    mock_response.content = VALID_OPML
    mock_response.raise_for_status.return_value = None

    mocker.patch("digest.core.requests.get", return_value=mock_response)

    feeds = get_feeds("http://valid.com/feeds.opml")
    assert len(feeds) == 2


def test_get_feeds_innaccessible_opml_url(mocker):
    mocker.patch("digest.core.requests.get", side_effect=requests.exceptions.ConnectionError("DNS Failure"))

    with pytest.raises(RuntimeError, match=r"Failed to fetch OPML: .*"):
        feeds = get_feeds("http://invalid.com/feeds.opml")


def test_get_feeds_invalid_opml_content(mocker):
    mock_response = mocker.Mock()
    mock_response.content = INVALID_OPML
    mock_response.raise_for_status.return_value = None

    mocker.patch("digest.core.requests.get", return_value=mock_response)

    with pytest.raises(RuntimeError, match=r"Failed to parse ML: .*"):
        feeds = get_feeds("http://valid.com/feeds.opml")


def test_get_feeds_empty_opml_content(mocker):
    mock_response = mocker.Mock()
    mock_response.content = EMPTY_OPML
    mock_response.raise_for_status.return_value = None

    mocker.patch("digest.core.requests.get", return_value=mock_response)

    with pytest.raises(RuntimeError, match="No valid feed found in OPML."):
        feeds = get_feeds("http://valid.com/feeds.opml")
