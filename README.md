# Digest

Digest is a simple tool to sum up a group of RSS feeds as a single markdown file on a regular basis.

## 📋 Description

Digest helps easily keep up with many news source feeds and summarize them. Those summarized news are saved in markdown format in the `news/` directory (automatically created if not existing). The aim of this project is to provide an easy way to automatically produce a weekly news digest from a group of RSS feeds.

## 📂 Project Structure

The project contains several files and directories, which are the following:

| Files | Description |
| :---- | :---------- |
| `news/<date>.md` | The markdown files containing the summarized news. |
| [`main.py`](https://github.com/gwendalminguy/tool-digest/blob/main/main.py) | The python script to summarize news from a group of RSS feeds. |
| [`install.sh`](https://github.com/gwendalminguy/tool-digest/blob/main/install.sh) | The bash script setting automations to launch the script on a regular basis. |
| [`instructions.md`](https://github.com/gwendalminguy/tool-digest/blob/main/instructions.md) | The markdown file containing AI instructions to produce a structured JSON output. |
| [`requirements.txt`](https://github.com/gwendalminguy/tool-digest/blob/main/requirements.txt) | The text file containing requirements to install. |

## 🔧 Prerequisites

Before installing Digest, make sure all of the following prerequisites are met:

**1. Programs**

Digest runs using `python3` and `crontab`. Both can be installed as follows:

```
$ sudo apt install python3
$ sudo apt install cron
```

**2. OPML URL**

...

**3. Gemini API Key**

...

## ⚙️ Installation

### Procedure

In order to install and use Digest, the three steps of this guide must be followed:

**1. Cloning the repository**

Clone this repository locally:

```
$ git clone https://github.com/gwendalminguy/tool-digest.git
```

**2. Installing the requirements**

Create and activate a virtual environment, then install dependencies:

```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements
```

**3. Setting the configuration**

To run Digest automatically on a regular basis, an scheduled task must be set (along with some configuration details). Run the installation script from the project root:

```
$ chmod u+x install.sh
$ ./install.sh
$ deactivate
```

The installation script will:
- ask for required configuration values
- create a `.env` file
- set up a cron job to run Digest periodically

The summarized news will be saved weekly as a markdown file in the `news/` directory. The user might be prompted by the system to authorize the automations, to allow the script execution.
