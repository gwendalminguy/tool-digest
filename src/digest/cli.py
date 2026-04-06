"""
cli.py
Module containing command-line interface functions.
"""
from digest.core import get_feeds, get_news, digest_news, generate_markdown
from datetime import datetime, timedelta
from dotenv import load_dotenv

import os
import stat
import subprocess
import sys
import typer


app = typer.Typer()

DAYS = {
    "sunday": 0,
    "monday": 1,
    "tuesday": 2,
    "wednesday": 3,
    "thursday": 4,
    "friday": 5,
    "saturday": 6,
}

LANGUAGES = [
    "fr"
]

@app.command()
def init(
    name: str = typer.Argument(help="Name of the project to configure."),
    language: str = typer.Option("fr", "--language", "-l", help="Language of the news.", min=0, max=23),
    opml_url: str = typer.Option(prompt=True, help="OPML URL of the group of RSS feeds to use."),
    gemini_api_key: str = typer.Option(prompt=True, hide_input=True, help="Gemini API key to use.")
):
    """
    Initialize a new project by generating a configuration file.
    """
    NAME = name.strip().lower()
    DIGEST_DIR = os.path.expanduser("~/.digest")
    OPML_URL = opml_url.strip()
    GEMINI_API_KEY = gemini_api_key.strip()
    NEWS_DIR = os.path.join(os.getcwd(), "news")
    INTERVAL = 7 # In days.
    LANGUAGE = language.lower()

    if LANGUAGE not in LANGUAGES:
        typer.echo("[ERROR] Invalid language.")
        raise typer.Exit(code=1)

    # Create necessary directories.
    os.makedirs(DIGEST_DIR, exist_ok=True)
    os.makedirs(NEWS_DIR, exist_ok=True)

    CONFIG_PATH = os.path.join(DIGEST_DIR, f"config.{NAME}.env")

    config = [
        f"NAME={NAME.upper()}",
        f"OPML_URL={OPML_URL}",
        f"GEMINI_API_KEY={GEMINI_API_KEY}",
        f"NEWS_PATH={NEWS_DIR}",
        f"INTERVAL={INTERVAL}",
        f"LANGUAGE={LANGUAGE}"
    ]

    # Confirm if configuration already exists.
    if os.path.exists(CONFIG_PATH):
        if not typer.confirm(f"[WARNING] {NAME} already exists. Overwrite?"):
            raise typer.Abort()

    # Create configuration file in ~/.digest/
    with open(CONFIG_PATH, "w", encoding="utf-8") as file:
        file.write("\n".join(config))

    # Set READ and WRITE permissions for user.
    os.chmod(CONFIG_PATH, stat.S_IRUSR | stat.S_IWUSR)

    typer.echo(f"[INFO] Digest configuration file created at: {CONFIG_PATH}")
    typer.echo(f"[INFO] News will be saved as markdown files in: {NEWS_DIR}")


@app.command()
def cron(
    name: str = typer.Argument(help="Name of the project to create a cronjob for."),
    time: int = typer.Option(9, "--time", "-t", help="Hour of the day.", min=0, max=23),
    day: str = typer.Option("sunday", "--day", "-d", help="Day of the week.")
):
    """
    Create a cronjob to run Digest every week for the specified project.
    """
    NAME = name.strip().lower()
    DIGEST_DIR = os.path.expanduser("~/.digest")
    CONFIG_PATH = os.path.join(DIGEST_DIR, f"config.{NAME}.env")
    PYTHON_PATH = sys.executable

    day = day.lower()

    if day not in DAYS:
        typer.echo("[ERROR] Invalid day.")
        raise typer.Exit(code=1)

    DAY = DAYS[day]

    if not os.path.exists(CONFIG_PATH):
        typer.echo("[INFO] Project not found. Run [digest init <name>] to initialize a new project.")
        return

    tag = f"# digest:{NAME}"
    command = f"0 {time} * * {DAY} {PYTHON_PATH} -m digest.cli run --silent {NAME} {tag}"

    # Retrieve all existing cronjobs.
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        current = result.stdout if result.returncode == 0 else ""
    except FileNotFoundError as e:
        typer.echo("[ERROR] Cron not installed. On Debian/Ubuntu, run [apt install cron] to install it.")
        raise typer.Exit(code=1)

    crontab = current.splitlines()

    for line in crontab:
        if line.strip().endswith(tag):
            typer.echo("[INFO] Cronjob already exists.")
            return

    # Rewrite existing crontab and add new one.
    crontab.append(f"{command}")
    new = "\n".join(crontab) + "\n"
    subprocess.run(["crontab", "-"], input=new, text=True)
    typer.echo(f"[INFO] Cronjob successfully added for {NAME}. Digest will run every {day.capitalize()} at {time}:00.")


@app.command()
def ls():
    """
    List all configured projects and their news output path.
    """
    DIGEST_DIR = os.path.expanduser("~/.digest")

    files = []
    content = []

    if os.path.isdir(DIGEST_DIR):
        files = [
            os.path.join(DIGEST_DIR, filename) for filename in os.listdir(DIGEST_DIR)
            if filename.startswith("config.") and filename.endswith(".env")
        ]

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
        typer.echo("[INFO] No project found. Run [digest init <name>] to initialize a new project.")


@app.command()
def rm(
    name: str = typer.Argument(help="Name of the project to delete.")
):
    """
    Remove a project configuration and its associated cronjob if existing.
    """
    NAME = name.strip().lower()
    DIGEST_DIR = os.path.expanduser("~/.digest")
    CONFIG_PATH = os.path.join(DIGEST_DIR, f"config.{NAME}.env")
    PYTHON_PATH = sys.executable

    if not os.path.exists(CONFIG_PATH):
        typer.echo("[INFO] Project not found. Run [digest init <name>] to initialize a new project.")
        return

    # Confirm removal.
    if not typer.confirm(f"[WARNING] Remove {NAME}?"):
        typer.echo("[INFO] Deletion cancelled.")
        raise typer.Abort()

    # Remove configuration file.
    os.remove(CONFIG_PATH)
    typer.echo(f"[INFO] Configuration file deleted for {NAME}.")

    # Remove cronjob.
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        current = result.stdout if result.returncode == 0 else ""
    except FileNotFoundError as e:
        return

    tag = f"# digest:{NAME}"

    # Rewrite existing crontab without the one to remove.
    crontab = current.splitlines()
    updated = [line for line in crontab if not line.strip().endswith(tag)]

    if len(updated) == len(crontab):
        typer.echo(f"[INFO] No cronjob found for {NAME}.")
        return

    new = "\n".join(updated) + "\n"
    subprocess.run(["crontab", "-"], input=new, text=True)
    typer.echo(f"[INFO] Cronjob deleted for {NAME}.")


@app.command()
def run(
    name: str = typer.Argument(help="Name of the project to run."),
    silent: bool = typer.Option(False, "--silent", "-s", help="Run in silent mode.")
):
    """
    Launch manually the summarization of recent news for a project.
    """
    NAME = name.strip().lower()
    DIGEST_DIR = os.path.expanduser("~/.digest")
    CONFIG_PATH = os.path.join(DIGEST_DIR, f"config.{NAME}.env")

    if os.path.isdir(DIGEST_DIR) and os.path.exists(CONFIG_PATH):
        load_dotenv(CONFIG_PATH)

        TODAY = datetime.now().strftime('%Y-%m-%d')
        INTERVAL = int(os.getenv("INTERVAL")) # In days.
        OPML_URL = os.getenv("OPML_URL")
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        LANGUAGE = os.getenv("LANGUAGE")

        feeds = get_feeds(OPML_URL)
        content = get_news(INTERVAL, feeds)
        result = digest_news(INTERVAL, LANGUAGE, GEMINI_API_KEY, content, silent)

        if result:
            generate_markdown(TODAY, result, silent)

    else:
        typer.echo("[INFO] Project not found. Run [digest init <name>] to initialize a new project.")


if __name__ == "__main__":
    app()
