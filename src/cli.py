"""
cli.py
Module containing command-line interface functions.
"""
from datetime import datetime, timedelta
from dotenv import load_dotenv
from core import get_feeds, get_news, digest_news, generate_markdown

import os
import typer


app = typer.Typer()

@app.command()
def init():
    """
    Initialize a new project with a configuration file.
    """
    NAME = typer.prompt("Project Name").strip().upper()
    OPML_URL = typer.prompt("OPML URL").strip()
    GEMINI_API_KEY = typer.prompt("Gemini API Key").strip()
    INTERVAL = 7 # In days.

    DIGEST_DIR = os.path.expanduser("~/.digest")
    NEWS_DIR = os.getcwd() + "/news"

    os.makedirs(DIGEST_DIR, exist_ok=True)
    os.makedirs(NEWS_DIR, exist_ok=True)

    config_path = os.path.join(DIGEST_DIR, f"config-{NAME.lower()}.env")

    config = [
        f"NAME={NAME}",
        f"OPML_URL={OPML_URL}",
        f"GEMINI_API_KEY={GEMINI_API_KEY}",
        f"NEWS_PATH={NEWS_DIR}",
        f"INTERVAL={INTERVAL}"
    ]

    with open(config_path, "w", encoding="utf-8") as file:
        file.write("\n".join(config))

    typer.echo(f"Digest configuration file created at: {config_path}")
    typer.echo(f"News will be saved as markdown files in: {NEWS_DIR}")


@app.command()
def run(name: str):
    """
    ...
    """
    DIGEST_DIR = os.path.expanduser("~/.digest")
    config_path = os.path.join(DIGEST_DIR, f"config-{name.lower()}.env")

    load_dotenv(config_path)

    TODAY = datetime.now().strftime('%Y-%m-%d')
    INTERVAL = int(os.getenv("INTERVAL")) # In days.
    OPML_URL = os.getenv("OPML_URL")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    feeds = get_feeds(OPML_URL)
    content = get_news(INTERVAL, feeds)
    result = digest_news(INTERVAL, GEMINI_API_KEY, content)

    if result:
        generate_markdown(TODAY, result)


if __name__ == "__main__":
    app()
