#!/venv/bin/python3
"""
core.py
Module containing core functions.
"""
from datetime import datetime, timedelta
from google import genai
from importlib import resources
from time import sleep
from xml.etree import ElementTree

import feedparser
import json
import os
import requests
import sys


def get_feeds(OPML_URL: str) -> list:
    """
    Retrieve every RSS feed URL from an OPML URL.
    """
    headers={
        "User-Agent": "Digest/0.1.0"
    }

    response = requests.get(
        OPML_URL,
        headers=headers
    )
    response.raise_for_status()

    root = ElementTree.fromstring(response.content)

    feeds = []

    # Retrieve the URL for each feed.
    for outline in root.iter('outline'):
        xml_url = outline.attrib.get('xmlUrl')
        title = outline.attrib.get('title')

        if xml_url:
            feeds.append({
                "title": title,
                "url": xml_url
            })

    return feeds


def get_news(INTERVAL: int, feeds: list) -> list:
    """
    Retrieve all articles from a list of RSS feed URLs for a given period of time.
    """
    NOW = datetime.now()
    WEEK = NOW - timedelta(days=INTERVAL)

    contents = [feedparser.parse(element["url"]) for element in feeds]
    news = []

    # Filter entries for each feed by date.
    for feed in contents:
        for entry in feed.entries:
            if "published_parsed" in entry:
                published = datetime(*entry.published_parsed[:6])
                if published > WEEK:
                    news.append({
                        "title": entry.title,
                        "link": entry.link,
                        "summary": entry.summary
                    })

    return news


def digest_news(INTERVAL: int, LANGUAGE: str, API_KEY:str, content: list, silent: bool) -> str | None:
    """
    Summarize as a structured JSON a list of articles.
    """
    client = genai.Client()
    success = False
    trial = 1

    # Get instructions from markdown file.
    filename = f"instructions_{LANGUAGE}.md"
    instructions = resources.files("digest.prompts").joinpath(filename).read_text()

    while trial <= 5:
        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=f"""
                    INSTRUCTIONS :
                    {instructions}

                    CONTENU À ANALYSER :
                    {content}
                """
            )

            success = True
            break

        except Exception as e:
            if not silent:
                print(f"Error (Trial {trial}): {e}")
            sleep(trial * 3)
            trial += 1

    if not success:
        sys.exit("Error: AI Service Unavailable")

    # Parse result.
    parts = response.candidates[0].content.parts
    raw = "".join(part.text for part in parts if hasattr(part, "text"))

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        if not silent:
            print("Error: Invalid JSON")
        return None

    return result


def generate_markdown(TODAY: int, digest: str, silent: bool):
    """
    Transform a structured JSON into a readable markdown file.
    """
    lines = []

    lines.append(f"# Weekly News: {TODAY}\n")

    # Build each section.
    for section in digest["summary"]:
        lines.append(f"## {section['category']}\n")

        for item in section["items"]:
            lines.append(f"- **{item['title']}**: {item['summary']}")

        lines.append("")

    # Create highlights section.
    if digest.get("highlights"):
        lines.append("## Highlights\n")
        for highlight in digest["highlights"]:
            lines.append(f"- {highlight}")

    result = "\n".join(lines)

    # Create directory if necessary.
    base = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(base, "news")
    os.makedirs(path, exist_ok=True)
    
    filename = f"{path}/{TODAY}.md"

    # Write digest to a file.
    with open(filename, "w", encoding="utf-8") as file:
        file.write(result)

    if not silent:
        print(f"[INFO] Digest created at: {filename}")
