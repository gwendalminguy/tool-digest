#!/venv/bin/python3
"""
core.py
Module containing core functions.
"""
from datetime import datetime, timedelta, timezone
from google import genai
from importlib import resources
from time import sleep, time
from xml.etree import ElementTree

import feedparser
import json
import os
import re
import requests
import sys


def get_feeds(OPML_URL: str) -> list:
    """
    Retrieve every RSS feed URL from an OPML URL.
    """
    start = time()
    headers={
        "User-Agent": "Digest/0.1.0"
    }

    # Fetch OPML.
    try:
        response = requests.get(
            OPML_URL,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to fetch OPML: {e}")

    # Parse XML.
    try:
        root = ElementTree.fromstring(response.content)
    except ElementTree.ParseError:
        raise RuntimeError("Failed to parse XML.")

    feeds = []

    # Retrieve the RSS URL for each feed.
    for outline in root.iter('outline'):
        xml_url = outline.attrib.get('xmlUrl')
        title = outline.attrib.get('title')

        if xml_url:
            feeds.append({
                "title": title,
                "url": xml_url
            })

    if not feeds:
        raise RuntimeError("No valid feed found in OPML.")

    end = time()
    length = round(end - start, 3)

    # print(f"[LOG] OPML: {length}s")

    return feeds


def get_news(INTERVAL: int, feeds: list, silent: bool) -> list:
    """
    Retrieve all articles from a list of RSS feed URLs for a given period of time.
    """
    NOW = datetime.now(timezone.utc)
    WEEK = NOW - timedelta(days=INTERVAL)

    start = time()
    news = []

    for element in feeds:
        category = element["title"]
        url = element["url"]

        feed = feedparser.parse(url)

        # Handle and log parsing errors.
        if feed.bozo:
            if not silent:
                print(f"[WARNING] Failed to parse feed: {url} ({feed.bozo_exception})")
            continue

        for entry in feed.entries:
            published = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)

            # Skip if no date found.
            if not published:
                continue

            # Respect timezone.
            published = datetime(*published[:6], tzinfo=timezone.utc)

            if published > WEEK:
                summary = getattr(entry, "summary", "No Summary")
                clean = re.sub(r"</?\w+[^>]*>", "", summary)

                news.append({
                    "category": category,
                    "title": getattr(entry, "title", "No Title"),
                    "link": getattr(entry, "link", "No Link"),
                    "summary": clean
                })

    # Dump result as JSON.
    # with open("news.json", "w", encoding="utf-8") as file:
        # json.dump(news, file, indent=4, ensure_ascii=False)

    end = time()
    length = round(end - start, 3)

    # print(f"[LOG] RSS: {length}s")

    return news


def digest_news(INTERVAL: int, LANGUAGE: str, API_KEY:str, content: list, silent: bool) -> dict:
    """
    Summarize as a structured JSON a list of articles.
    """
    start = time()
    client = genai.Client(api_key=API_KEY)
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

                    CONTENT :
                    {content}
                """
            )

            success = True
            break

        except Exception as e:
            if not silent:
                print(f"Error (Trial {trial}): {e}")
            sleep(2 ** trial)
            trial += 1

    if not success:
        raise RuntimeError("AI Service Unavailable.")

    if not response.candidates:
        raise RuntimeError("Empty response from AI.")

    # Parse result.
    parts = response.candidates[0].content.parts or []
    raw = "".join(part.text for part in parts if hasattr(part, "text"))

    if not raw:
        raise RuntimeError("Empty content returned by AI.")

    raw = raw.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        raise RuntimeError("Invalid JSON.")

    # Dump result as JSON.
    # with open("digest.json", "w", encoding="utf-8") as file:
        # json.dump(result, file, indent=4, ensure_ascii=False)

    end = time()
    length = round(end - start, 3)

    # print(f"[LOG] GEMINI: {length}s")

    return result


def generate_markdown(TODAY: int, NEWS_PATH: str, digest: dict) -> str:
    """
    Transform a structured JSON into a readable markdown file.
    """
    lines = []

    lines.append(f"# Weekly News: {TODAY}\n")

    # Create highlights section.
    if digest.get("highlights"):
        lines.append("## Highlights\n")
        for highlight in digest["highlights"]:
            lines.append(f"- {highlight}")

        lines.append("")

    # Create details section and build each category.
    lines.append("## Details\n")
    for section in digest["summary"]:
        lines.append(f"- ### {section['category']}\n")

        for item in section["items"]:
            lines.append(f"  - **[{item['title']}]({item['link']})**: {item['summary']}")

        lines.append("")

    result = "\n".join(lines)
    
    filename = os.path.join(NEWS_PATH, f"{TODAY}.md")

    # Write digest to a file.
    with open(filename, "w", encoding="utf-8") as file:
        file.write(result)

    return filename
