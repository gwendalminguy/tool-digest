"""
cli.py
Module containing command-line interface functions.
"""
from digest.core import get_feeds, get_news, digest_news, generate_markdown
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

import os
import re
import stat
import shutil
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

DAYS_REVERSE =  {
    str(value): key for key, value in DAYS.items()
}

FREQUENCIES = [
    "weekly",
    "monthly"
]

LANGUAGES = {
    "de": "german",
    "en": "english",
    "es": "spanish",
    "fr": "french",
    "hi": "hindi",
    "it": "italian",
    "ja": "japanese",
    "pt": "portuguese",
    "ru": "russian",
    "zh": "chinese"
}

@app.command()
def init(
    name: str = typer.Argument(help="Name of the project to configure."),
    opml_url: str = typer.Option(prompt=True, help="OPML URL of the group of RSS feeds to use."),
    api_key: str = typer.Option(prompt=True, hide_input=True, help="Google API key to use."),
    path: str = typer.Option("news", "--path", "-p", help="Path to Digest output directory."),
    language: str = typer.Option("en", "--language", "-l", help="Language of the news."),
    frequency: str = typer.Option("weekly", "--frequency", "-f", help="Default frequency (weekly|monthly).")
):
    """
    Initialize a new project by generating a configuration file.
    """
    NAME = name.strip().lower()
    DIGEST_DIR = os.path.expanduser("~/.digest")
    CONFIG_PATH = os.path.join(DIGEST_DIR, f"config.{NAME}.env")

    OPML_URL = opml_url.strip()
    API_KEY = api_key.strip()
    NEWS_PATH = os.path.abspath(path)
    LANGUAGE = language.lower()
    FREQUENCY = frequency.lower()

    if not re.match("^[a-z0-9][a-z0-9_-]*$", NAME):
        typer.echo("[ERROR] Invalid name.")
        raise typer.Exit(code=1)

    if LANGUAGE not in LANGUAGES.keys():
        typer.echo("[ERROR] Invalid language.")
        raise typer.Exit(code=1)

    if FREQUENCY not in FREQUENCIES:
        typer.echo("[ERROR] Invalid frequency (weekly|monthly).")
        raise typer.Exit(code=1)

    if os.path.exists(NEWS_PATH) and not os.path.isdir(NEWS_PATH):
        typer.echo("[ERROR] Path exists but is not a directory.")
        raise typer.Exit(code=1)

    # Create Digest directory.
    try:
        os.makedirs(DIGEST_DIR, exist_ok=True)
    except OSError:
        typer.echo("[ERROR] Unable to create Digest directory.")
        raise typer.Exit(code=1)

    # Create output directory.
    try:
        os.makedirs(NEWS_PATH, exist_ok=True)
    except OSError:
        typer.echo("[ERROR] Unable to create output directory.")
        raise typer.Exit(code=1)

    config = [
        f"NAME={NAME.upper()}",
        f"OPML_URL={OPML_URL}",
        f"API_KEY={API_KEY}",
        f"NEWS_PATH={NEWS_PATH}",
        f"LANGUAGE={LANGUAGE}",
        f"FREQUENCY={FREQUENCY}"
    ]

    # Confirm if configuration already exists.
    if os.path.exists(CONFIG_PATH):
        if not typer.confirm(f"[WARNING] {NAME} already exists. Overwrite?"):
            raise typer.Abort()

    # Create configuration file in ~/.digest/
    with open(CONFIG_PATH, "w", encoding="utf-8") as file:
        file.write("\n".join(config) + "\n")

    # Set READ and WRITE permissions for user.
    os.chmod(CONFIG_PATH, stat.S_IRUSR | stat.S_IWUSR)

    typer.echo(f"[INFO] Digest configuration file created at: {CONFIG_PATH}")
    typer.echo(f"[INFO] News will be saved as markdown files in {LANGUAGES[LANGUAGE].capitalize()} at: {NEWS_PATH}")


@app.command()
def edit(
    name: str = typer.Argument(help="Name of the project to edit."),
    force: bool = typer.Option(False, "--force", "-f", help="No confirmation prompt before edition."),
    opml_url: str = typer.Option(None, "--opml-url", "-o", help="OPML URL of the group of RSS feeds to use."),
    api_key: str = typer.Option(None, "--api-key", "-a", hide_input=True, help="Google API key to use."),
    path: str = typer.Option(None, "--path", "-p", help="Path to Digest output directory."),
    language: str = typer.Option(None, "--language", "-l", help="Language of the news."),
    frequency: str = typer.Option(None, "--frequency", "-F", help="Default frequency (weekly|monthly).")
):
    """
    Edit the configuration of an existing project.
    """
    NAME = name.strip().lower()
    DIGEST_DIR = os.path.expanduser("~/.digest")
    CONFIG_PATH = os.path.join(DIGEST_DIR, f"config.{NAME}.env")

    OPML_URL = opml_url.strip() if opml_url else None
    API_KEY = api_key.strip() if api_key else None
    NEWS_PATH = os.path.abspath(path) if path else None
    LANGUAGE = language.lower() if language else None
    FREQUENCY = frequency.lower() if frequency else None

    if not re.match("^[a-z0-9][a-z0-9_-]*$", NAME):
        typer.echo("[ERROR] Invalid name.")
        raise typer.Exit(code=1)

    if not os.path.exists(CONFIG_PATH):
        typer.echo(f"[INFO] Project not found. To initialize it as a new project, run `digest init {NAME}`")
        return

    changed = {
        "OPML URL": OPML_URL is not None,
        "API Key": API_KEY is not None,
        "News Path": NEWS_PATH is not None,
        "Language": LANGUAGE is not None,
        "Frequency": FREQUENCY is not None,
    }

    # Load configuration file.
    load_dotenv(CONFIG_PATH, override=False)

    if not LANGUAGE:
        LANGUAGE = os.getenv("LANGUAGE")

    if not NEWS_PATH:
        NEWS_PATH = os.getenv("NEWS_PATH")

    if not OPML_URL:
        OPML_URL = os.getenv("OPML_URL")

    if not API_KEY:
        API_KEY = os.getenv("API_KEY")

    if not FREQUENCY:
        FREQUENCY = os.getenv("FREQUENCY")

    if LANGUAGE not in LANGUAGES.keys():
        typer.echo("[ERROR] Invalid language.")
        raise typer.Exit(code=1)

    if FREQUENCY not in FREQUENCIES:
        typer.echo("[ERROR] Invalid frequency (weekly|monthly).")
        raise typer.Exit(code=1)

    if os.path.exists(NEWS_PATH) and not os.path.isdir(NEWS_PATH):
        typer.echo("[ERROR] Path exists but is not a directory.")
        raise typer.Exit(code=1)

    # Create output directory.
    try:
        os.makedirs(NEWS_PATH, exist_ok=True)
    except OSError:
        typer.echo("[ERROR] Unable to create output directory.")
        raise typer.Exit(code=1)

    config = [
        f"NAME={NAME.upper()}",
        f"OPML_URL={OPML_URL}",
        f"API_KEY={API_KEY}",
        f"NEWS_PATH={NEWS_PATH}",
        f"LANGUAGE={LANGUAGE}",
        f"FREQUENCY={FREQUENCY}"
    ]

    elements = [key for key, value in changed.items() if value]

    # Confirm changes.
    if elements:
        if not force and not typer.confirm(f"[WARNING] Update {', '.join(elements)} for {NAME}?"):
            raise typer.Abort()
    else:
        typer.echo(f"[ERROR] No change made. To edit an existing project, run `digest edit {NAME} <option> <value>`")
        raise typer.Exit(code=1)

    # Warn for potential cronjob mismatch.
    if changed["Frequency"]:
        typer.echo(
            f"[WARNING] Changed frequency to {'weekly' if FREQUENCY == "weekly" else 'monthly'} mode. "
            f"If a cronjob already exists for {NAME}, it may now be out of sync. "
            f"To regenerate it, run `digest cron {NAME} [-d <day> -h <hour>]`"
        )

    # Overwrite configuration file in ~/.digest/
    with open(CONFIG_PATH, "w", encoding="utf-8") as file:
        file.write("\n".join(config) + "\n")

    typer.echo(f"[INFO] Configuration file updated for {NAME}.")


@app.command()
def cron(
    name: str = typer.Argument(help="Name of the project to create a cronjob for."),
    hour: int = typer.Option(9, "--hour", "-H", help="Execution hour (1-23).", min=0, max=23),
    day: str = typer.Option(None, "--day", "-d", help="Execution day (weekly: monday-sunday, monthly: 1-28).")
):
    """
    Create a cronjob to run Digest weekly or monthly for the specified project.
    """
    NAME = name.strip().lower()
    DIGEST_DIR = os.path.expanduser("~/.digest")
    CONFIG_PATH = os.path.join(DIGEST_DIR, f"config.{NAME}.env")
    DIGEST_PATH = shutil.which("digest")

    if not os.path.exists(CONFIG_PATH):
        typer.echo(f"[INFO] Project not found. To initialize a new project, run `digest init {NAME}`")
        return

    # Load configuration file.
    load_dotenv(CONFIG_PATH, override=False)

    FREQUENCY = os.getenv("FREQUENCY")
    
    if FREQUENCY not in FREQUENCIES:
        typer.echo(f"[ERROR] No frequency found. To define it, run `digest edit {NAME} --frequency weekly|monthly`")
        raise typer.Exit(code=1)

    if not re.match("^[a-z0-9][a-z0-9_-]*$", NAME):
        typer.echo("[ERROR] Invalid name.")
        raise typer.Exit(code=1)

    # Weekly Mode
    if FREQUENCY == "weekly":
        if not day:
            day = "sunday"
        if day.lower() not in DAYS:
            typer.echo("[ERROR] Invalid day.")
            raise typer.Exit(code=1)

        DAY_WEEK = DAYS[day.lower()]
        DAY_MONTH = "*"

    # Monthly Mode
    elif FREQUENCY == "monthly":
        if not day:
            day = 1
        else:
            try:
                day = int(day)
            except ValueError:
                typer.echo("[ERROR] Invalid day (1-28).")
                raise typer.Exit(code=1)
        if day < 1 or day > 28:
            typer.echo("[ERROR] Invalid day (1-28).")
            raise typer.Exit(code=1)

        DAY_WEEK = "*"
        DAY_MONTH = day

    # Define tag and cronjob expression.
    tag = f"# digest:{NAME}"
    command = f"0 {hour} {DAY_MONTH} * {DAY_WEEK} {DIGEST_PATH} run {NAME} --silent {tag}"

    # Retrieve all existing cronjobs.
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        current = result.stdout if result.returncode == 0 else ""
    except FileNotFoundError as e:
        typer.echo("[ERROR] Cron not installed. To install it on Debian/Ubuntu, run `apt install cron`")
        raise typer.Exit(code=1)

    crontab = current.splitlines()

    for line in crontab:
        if line.strip().endswith(tag):
            if not typer.confirm(f"[WARNING] Cronjob for {NAME} already exists. Overwrite?"):
                raise typer.Abort()

            # Remove deprecated line
            crontab[:] = [item for item in crontab if not item.strip().endswith(tag)]

    # Rewrite existing crontab and add new one.
    crontab.append(f"{command}")
    new = "\n".join(crontab) + "\n"
    subprocess.run(["crontab", "-"], input=new, text=True)

    # Weekly Mode
    if FREQUENCY == "weekly":
        typer.echo(f"[INFO] Cronjob successfully generated for {NAME}. Digest will run every {day.capitalize()} at {hour}:00.")

    # Monthly Mode
    elif FREQUENCY == "monthly":
        typer.echo(f"[INFO] Cronjob successfully generated for {NAME}. Digest will run on the {day} of every month at {hour}:00.")


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

    if not files:
        typer.echo("[INFO] No project found. To initialize a new project, run `digest init <name>`")
        return

    # Retrieve cronjobs.
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        current = result.stdout if result.returncode == 0 else ""
        crontab = current.splitlines()
    except FileNotFoundError as e:
        crontab = None

    # Get name and news directory for each project.
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

            cronjob = "None"

            # Get cronjob if one is configured.
            if crontab:
                tag = f"# digest:{name.lower()}"
                for line in crontab:
                    if line.strip().endswith(tag):
                        moment = line.strip().split(" ")[:5]
                        hour = f"{moment[1]}:00"
                        if moment[2] != "*":
                            day = moment[2]
                            cronjob = f"Day {day} at {hour}"
                        elif moment[4] != "*":
                            day = DAYS_REVERSE.get(moment[4], "Unknown").capitalize()
                            cronjob = f"{day} at {hour}"
                        break

            content.append({
                "name": name,
                "news": news_path,
                "cronjob": cronjob
            })

    # Compute column widths
    name_width = max(len(project["name"]) for project in content + [{"name": "NAME"}])
    path_width = max(len(project["news"]) for project in content + [{"news": "OUTPUT DIRECTORY"}])
    cron_width = max(len(project["cronjob"]) for project in content + [{"cronjob": "CRONJOB"}])

    # Define horizontal separators
    separator_sup = f"┌{'─' * (name_width + 2)}┬{'─' * (path_width + 2)}┬{'─' * (cron_width + 2)}┐"
    separator_mid = f"├{'─' * (name_width + 2)}┼{'─' * (path_width + 2)}┼{'─' * (cron_width + 2)}┤"
    separator_inf = f"└{'─' * (name_width + 2)}┴{'─' * (path_width + 2)}┴{'─' * (cron_width + 2)}┘"

    # Print header
    typer.echo(separator_sup)
    typer.echo(
        f"│ {'NAME':<{name_width}} "
        f"│ {'OUTPUT DIRECTORY':<{path_width}} "
        f"│ {'CRONJOB':<{cron_width}} │"
    )

    typer.echo(separator_mid)

    # Print rows
    for project in content:
        typer.echo(
            f"│ {project['name']:<{name_width}} "
            f"│ {project['news']:<{path_width}} "
            f"│ {project['cronjob']:<{cron_width}} │"
        )

    typer.echo(separator_inf)


@app.command()
def rm(
    name: str = typer.Argument(help="Name of the project to delete."),
    force: bool = typer.Option(False, "--force", "-f", help="No confirmation prompt before deletion.")
):
    """
    Remove a project configuration and its associated cronjob if existing.
    """
    NAME = name.strip().lower()
    DIGEST_DIR = os.path.expanduser("~/.digest")
    CONFIG_PATH = os.path.join(DIGEST_DIR, f"config.{NAME}.env")

    if not re.match("^[a-z0-9][a-z0-9_-]*$", NAME):
        typer.echo("[ERROR] Invalid name.")
        raise typer.Exit(code=1)

    if not os.path.exists(CONFIG_PATH):
        typer.echo(f"[INFO] Project not found. To initialize a new project, run `digest init {NAME}`")
        return

    # Confirm removal.
    if not force:
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

    if not re.match("^[a-z0-9][a-z0-9_-]*$", NAME):
        typer.echo("[ERROR] Invalid name.")
        raise typer.Exit(code=1)

    if not os.path.exists(CONFIG_PATH):
        if not silent:
            typer.echo(f"[INFO] Project not found. To initialize a new project, run `digest init {NAME}`")
        return

    # Load configuration file.
    load_dotenv(CONFIG_PATH, override=False)

    NOW = datetime.now(timezone.utc)
    OPML_URL = os.getenv("OPML_URL")
    API_KEY = os.getenv("API_KEY")
    NEWS_PATH = os.getenv("NEWS_PATH")
    LANGUAGE = LANGUAGES[os.getenv("LANGUAGE", "en")]
    FREQUENCY = os.getenv("FREQUENCY")
    
    if FREQUENCY not in FREQUENCIES:
        typer.echo(f"[ERROR] No frequency found. To define one, run `digest edit {NAME} --frequency weekly|monthly`")
        raise typer.Exit(code=1)

    if not OPML_URL or not API_KEY or not NEWS_PATH:
        if not silent:
            typer.echo("[ERROR] Missing required configuration.")
        return

    # Weekly Mode
    if FREQUENCY == "weekly":
        INTERVAL = 7

    # Monthly Mode
    elif FREQUENCY == "monthly":
        INTERVAL = 30

    # Dates Window
    DATES = (NOW - timedelta(days=INTERVAL), NOW)

    try:
        feeds = get_feeds(OPML_URL)
        content = get_news(DATES, feeds, silent)
        news = digest_news(LANGUAGE, API_KEY, content, silent)
    except RuntimeError as e:
        if not silent:
            typer.echo(f"[ERROR] {e}")
        return

    length = (len(content), len(feeds))

    if news:
        filename = generate_markdown(DATES, NEWS_PATH, news, length)
        if not silent:
            typer.echo(f"[INFO] Digest generated successfully at: {filename}")


if __name__ == "__main__":
    app()
