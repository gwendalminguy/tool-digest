"""
test_generate_markdown.py
Tests for generate_markdown core function.
"""
from datetime import datetime, timezone
from digest.core import generate_markdown


DATES = (
    datetime(2026, 7, 17, tzinfo=timezone.utc),
    datetime(2026, 7, 24, tzinfo=timezone.utc)
)

COMPLETE_JSON = {
  "summary": [
    {
      "category": "Category Name", 
      "items": [
        {
          "title": "Article A",
          "summary": "Description A",
          "link": "http://example.com/a"
        },
        {
          "title": "Article B",
          "summary": "Description B",
          "link": "http://example.com/b"
        }
      ]
    }
  ],
  "highlights": ["Highlight 1", "Highlight 2"]
}

INCOMPLETE_JSON = {
  "summary": [
    {
      "category": "Category Name", 
      "items": [
        {},
        {"title": "Title Only"},
        {"summary": "Description Only"},
        {"link": "http://example.com/link/only"}
      ]
    }
  ],
  "highlights": []
}


def test_generate_markdown_complete_json_output(tmp_news_dir):
    generate_markdown(DATES, str(tmp_news_dir), COMPLETE_JSON, (2, 1))

    file_name = f"{DATES[1].strftime('%Y-%m-%d')}.md"
    file_path = tmp_news_dir / file_name
    
    content = file_path.read_text(encoding="UTF-8")

    # Header Section
    assert "# Digest - 24 July 2026" in content
    assert "**Period:** 2026-07-17 • 2026-07-24" in content
    assert "**Source:** 2 articles from 1 feeds." in content

    # Highlights Section
    assert "## Highlights" in content
    assert "- Highlight 1" in content
    assert "- Highlight 2" in content

    # Details Section
    assert "## Details" in content
    assert "### Category Name" in content
    assert "[Article A](http://example.com/a)" in content
    assert "Description A" in content
    assert "[Article B](http://example.com/b)" in content
    assert "Description B" in content


def test_generate_markdown_incomplete_json_output(tmp_news_dir):
    generate_markdown(DATES, str(tmp_news_dir), INCOMPLETE_JSON, (2, 1))

    file_name = f"{DATES[1].strftime('%Y-%m-%d')}.md"
    file_path = tmp_news_dir / file_name
    
    content = file_path.read_text(encoding="UTF-8")

    # Incomplete Item Handled
    assert "**[Title Only](#)**: *No Content*" in content
    assert "**[*Untitled*](http://example.com/link/only)**: *No Content*" in content
    assert "**[*Untitled*](#)**: Description Only" in content

    # Empty Item Ignored
    assert "**[*Untitled*](#)**: *No Content*" not in content
