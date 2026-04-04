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
| [`instructions.md`](https://github.com/gwendalminguy/tool-digest/blob/main/instructions.md) | The markdown file containing instructions to guide AI into producing a structured JSON output. |
| [`requirements.txt`](https://github.com/gwendalminguy/tool-digest/blob/main/requirements.txt) | The text file containing requirements to install. |

## ⚙️ Installation

In order to install Digest, the three steps of this guide must be followed:

**1. Cloning the repository**

To use Digest, this repository must be cloned locally, using the following command:

```
$ git clone https://github.com/gwendalminguy/tool-digest.git
```

**2. Installing the requirements**

A virtual environment mus be created in order to install the requirements:

```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements
```

**3. Setting the configuration**

To let Digest run on a regular basis, an automation must be set, along with some configuration details. This can be achieved by launching the `install.sh` bash script, and must be done at the root of the Digest directory, using these commands:

```
$ chmod u+x install.sh
$ ./install.sh
$ deactivate
```

This will allow the execution on a regular schedule of the `main.py` script. The summarized news will be saved weekly as a markdown file in the `news/` directory. The user might be prompted by the system to authorize the automations, to allow the script execution.
