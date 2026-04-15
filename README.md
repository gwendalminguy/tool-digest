# Digest

Digest is a simple tool to summarize a group of RSS feeds as a single markdown file on a regular basis.

## Description

Digest helps easily keep up with many news source feeds and summarize them. Those summarized news are saved in markdown format in the `news/` directory (automatically created if not existing). The aim of this project is to provide an easy way to automatically produce a weekly news digest from a group of RSS feeds.

## Flow Logic

On launch, Digest works as follow:

1. Fetch RSS feeds from the provided OPML URL
2. Filter recent articles (seven last days)
3. Send them to Gemini for summarization
4. Generate a structured markdown file

## Example Output

The is what the markdown file output looks like:

> # Digest - 15 April 2026
>
> **Period:** 2026-04-08 • 2026-04-15 \
> **Source:** 9 articles from 12 feeds.
>
> ## Highlights
>
> - Bun v1.3.12 introduces native Markdown rendering and built-in cron scheduling.
> - New security integrations in Docker allow for smarter vulnerability prioritization via VEX statements.
> - Real-time data migration and cross-database querying are now easier with DBConvert Streams 2.0.
> - Pydantic v2.13.0 provides early support for Python 3.14 in its v1 namespace.
> - React improves Server Components stability with new cycle protection mechanisms.
> - ShadCN UI enhances DX with project preset switching and structured component trees.
> - Uvicorn adds WebSocket keepalive pings to improve long-lived connection reliability.
>
> ## Details
>
> - ### Bun
>
>   - **[Bun v1.3.12: Markdown rendering, cron scheduler, and faster performance](https://bun.com/blog/bun-v1.3.12)**: Introduces Bun.WebView for headless automation and Bun.cron for in-process scheduling. Enhances performance for URLPattern and Glob scanning by over 2x.
>
> - ### Docker
>
>   - **[Docker and Mend.io integration for vulnerability prioritization](https://www.docker.com/blog/reclaim-developer-hours-through-smarter-vulnerability-prioritization-with-docker-and-mend-io/)**: Uses VEX statements to distinguish between exploitable and non-exploitable vulnerabilities in Hardened Images. Helps developers focus on high-impact security risks.
>
> - ### PostgreSQL
>
>   - **[DBConvert Streams 2.0: Real-time CDC and federated queries](https://www.postgresql.org/about/news/dbconvert-streams-20-released-with-postgresql-cdc-and-cross-database-querying-3268/)**: Enables continuous data replication using PostgreSQL WAL without external pipelines like Kafka. Supports cross-database querying and automatic schema conversion.
>
> - ### Pydantic
>
>   - **[Pydantic v2.13.0: Python 3.14 Support](https://github.com/pydantic/pydantic/releases/tag/v2.13.0)**: Updates the pydantic.v1 namespace to support Python 3.14 and includes jiter updates to fix Linux segmentation faults. Allows private attribute default factories to access validated model data.
>
> - ### React
>
>   - **[React 19 Security: Cycle protections for Server Components](https://github.com/facebook/react/releases/tag/v19.0.5)**: Versions 19.0.5, 19.1.6, and 19.2.5 introduce enhanced cycle protections. Targeted specifically at improving React Server Components stability.
>
> - ### ShadCN UI
>
>   - **[New shadcn apply command and Component Composition](https://ui.shadcn.com/docs/changelog/2026-04-shadcn-apply)**: Introduces the ability to switch presets in existing projects without manual restarts. Adds structured composition trees to assist both developers and AI agents.
>
> - ### Uvicorn
>
>   - **[Uvicorn 0.44.0: WebSocket keepalive support](https://github.com/Kludex/uvicorn/releases/tag/0.44.0)**: Implements keepalive pings for the websockets-sansio implementation. Improves connection stability for long-lived websocket sessions.

## Project Structure

The project contains several files and directories, which are the following:

| Files | Description |
| :---- | :---------- |
| [`src/digest/cli.py`](https://github.com/gwendalminguy/tool-digest/blob/main/src/digest/cli.py) | The python module containing command-line interface functions. |
| [`src/digest/core.py`](https://github.com/gwendalminguy/tool-digest/blob/main/src/digest/core.py) | The python module containing core functions. |
| [`src/digest/instructions.md`](https://github.com/gwendalminguy/tool-digest/blob/main/src/digest/prompts/) | The markdown files containing AI instructions to produce a structured JSON output. |
| [`LICENSE`](https://github.com/gwendalminguy/tool-digest/blob/main/LICENSE) | The license file. |
| [`pyproject.toml`](https://github.com/gwendalminguy/tool-digest/blob/main/pyproject.toml) | The packaging configuration file. |
| [`requirements.txt`](https://github.com/gwendalminguy/tool-digest/blob/main/requirements.txt) | The text file containing requirements to install. |

## Prerequisites

Before installing Digest, make sure all of the following prerequisites are met:

**1. OPML URL**

To give Digest a source for the feeds to summarize, an OPML URL is required. It can be generated by using an external RSS tool (such as [Inoreader](https://www.inoreader.com), [Feedly](https://feedly.com), etc.).

**2. Google API Key**

The news summarization is achieved by making an external call to **Gemini 3 Flash Preview**. An API key is therefore required, it can be generated [here](https://ai.google.dev/gemini-api/docs/api-key?hl=fr).

**3. Scheduling**

In order to schedule Digest so that it can run automatically, `crontab` is required. On Debian/Ubuntu, it can be installed as follows:

```bash
$ sudo apt install cron
```

## Installation

It is recommended to create a virtual environment before installing Digest:

```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install tool-digest
```

## Configuration

To initialize a new Digest, run:

```bash
$ digest init <name>    [--language en --path news/]        # Initialize a new Digest with a name.
```

During initialization, the user will be prompted for:

- an OPML URL (RSS feeds source)
- a Gemini API Key

On initialization of a new Digest, a configuration is created at `~/.digest/config.<name>.env`, and a `news/` directory is created (where the `init` command is launched when no specific path is specified), in which the summarized news will be saved as a markdown file.

To configure this Digest to launch weekly, run:

```bash
$ digest cron <name>    [--day monday --hour 9]             # Schedule a cronjob to run a Digest automatically every week.
```

Even if a cronjob has been set, the virtual environment can be still be deactivated once Digest has been configured, it will still run automatically as expected. Do not delete the virtual environment though, or the cronjob will fail. If you want to delete the virtual environment, make sure you remove any Digest-related cronjob before.

## Usage

Once a Digest is configured, the following commands can be used:

### Run

```bash
$ digest run <name>                         [--silent]      # Run Digest to summarize a group of RSS feeds.
```

### Manage

```bash
$ digest edit <name> <option> <value>       [--force]       # Edit a Digest by updating its configuration file.
$ digest rm <name>                          [--force]       # Remove a Digest by deleting its configuration file and its cronjob if it exists.
$ digest ls                                                 # List each configured Digest and its news/ output path, as well as the related cronjob if it exists.
```

### Help

```bash
$ digest --help                                             # Show help with description for available commands.
$ digest <command> --help                                   # Show help with arguments/options description for the specified command.
```

## Warning

Once a Digest created, it is recommended not to manually edit its configuration file located in the `~/.digest/` directory, as it may lead to unexpected behavior. To safely change the configuration of a Digest, use the dedicated `digest edit <name>` command.
