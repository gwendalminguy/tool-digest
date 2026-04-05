"""
cli.py
Module containing command-line interface functions.
"""
from datetime import datetime, timedelta
from dotenv import load_dotenv
from core import get_feeds, get_news, digest_news, generate_markdown

import os
import stat
import typer


app = typer.Typer()

@app.command()
def init(name: str):
    """
    Initialize a new project by generating a configuration file.
    """
    DIGEST_DIR = os.path.expanduser("~/.digest")
    OPML_URL = typer.prompt("OPML URL").strip()
    GEMINI_API_KEY = typer.prompt("Gemini API Key").strip()
    NEWS_DIR = os.getcwd() + "/news"
    INTERVAL = 7 # In days.

    # Create necessary directories.
    os.makedirs(DIGEST_DIR, exist_ok=True)
    os.makedirs(NEWS_DIR, exist_ok=True)

    CONFIG_PATH = os.path.join(DIGEST_DIR, f"config.{name.strip().lower()}.env")

    config = [
        f"NAME={name.strip().upper()}",
        f"OPML_URL={OPML_URL}",
        f"GEMINI_API_KEY={GEMINI_API_KEY}",
        f"NEWS_PATH={NEWS_DIR}",
        f"INTERVAL={INTERVAL}"
    ]

    # Create configuration file in ~/.digest/
    with open(CONFIG_PATH, "w", encoding="utf-8") as file:
        file.write("\n".join(config))

    # Set READ and WRITE permissions for user.
    os.chmod(CONFIG_PATH, stat.S_IRUSR | stat.S_IWUSR)

    typer.echo(f"Digest configuration file created at: {CONFIG_PATH}")
    typer.echo(f"News will be saved as markdown files in: {NEWS_DIR}")


@app.command()
def ls():
    """
    List all configured projects and their news output path.
    """
    DIGEST_DIR = os.path.expanduser("~/.digest")

    files = []
    content = []

    if os.path.isdir(DIGEST_DIR):
        files = [os.path.join(DIGEST_DIR, filename) for filename in os.listdir(DIGEST_DIR)]

    # Get name and news directory for each project.
    if files:
        for file_path in files:
            name = ""
            news_path = ""

            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    key, _, value = line.partition("=")

                    if key == "NAME":
                        name = value
                    elif key == "NEWS_PATH":
                        news_path = value

                content.append({
                    "Name": name,
                    "News": news_path
                })

        # Print name and news directory for each project.
        for project in content:
            typer.echo(f"- {project['Name']:<15} {project['News']}")

    else:
        typer.echo("No project found. Run [digest init <name>] to initialize a new project.")


@app.command()
def rm(name: str):
    """
    Remove a project configuration file.
    """
    DIGEST_DIR = os.path.expanduser("~/.digest")
    CONFIG_PATH = os.path.join(DIGEST_DIR, f"config.{name.strip().lower()}.env")

    if os.path.isdir(DIGEST_DIR) and os.path.exists(CONFIG_PATH):
        confirmation = typer.confirm(f"Remove {name.strip().lower()}?")

        if confirmation:
            os.remove(CONFIG_PATH)
            typer.echo("Deleted.")
        else:
            typer.echo("Deletion cancelled.")
            raise typer.Abort()

    else:
        typer.echo("Project not found. Run [digest init <name>] to initialize a new project.")


@app.command()
def run(name: str):
    """
    Launch manually the summarization of recent news for a project.
    """
    DIGEST_DIR = os.path.expanduser("~/.digest")
    CONFIG_PATH = os.path.join(DIGEST_DIR, f"config.{name.strip().lower()}.env")

    if os.path.isdir(DIGEST_DIR) and os.path.exists(CONFIG_PATH):
        load_dotenv(CONFIG_PATH)

        TODAY = datetime.now().strftime('%Y-%m-%d')
        INTERVAL = int(os.getenv("INTERVAL")) # In days.
        OPML_URL = os.getenv("OPML_URL")
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

        feeds = get_feeds(OPML_URL)
        content = get_news(INTERVAL, feeds)
        result = digest_news(INTERVAL, GEMINI_API_KEY, content)

        if result:
            generate_markdown(TODAY, result)

    else:
        typer.echo("Project not found. Run [digest init <name>] to initialize a new project.")


if __name__ == "__main__":
    app()
