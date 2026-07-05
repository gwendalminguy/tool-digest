# Changelog

This document tracks the history for notable changes to **Digest**.

## [0.2.0] - 2026-07-05

### Breaking Changes

- Removed `INTERVAL` configuration key and `--interval` option from `digest init` and `digest edit` commands
- `digest cron` command reads cadence from new `FREQUENCY` configuration key
- `--day` is now polymorphic, and has to be a string in `weekly` mode (`monday`, etc.), and an integer in `monthly` mode (`1`–`28`)

### Features

- New `FREQUENCY` configuration key (`weekly` or `monthly`)
- New `--frequency` option for `digest init` and `digest edit`
- `digest cron` now supports both **weekly** and **monthly** schedules (based on `FREQUENCY`)
- `digest ls` now displays weekly and monthly cronjobs correctly

### Migration

Existing projects from vesion **0.1.0** using `INTERVAL` are silently ignored. To migrate:

```bash
$ digest edit <name> --frequency weekly

# OR

$ digest edit <name> --frequency monthly
```

Then, if a cronjob exists for this Digest, overwrite it so the schedule matches the new cadence:

```bash
$ digest cron <name> [--day <day> --hour <hour>]
```

## [0.1.0] - 2026-04-15

Initial release of **Digest**, a CLI tool to generate structured summaries from RSS feeds using AI.

### Features

- OPML-based RSS feed aggregation
- News summarization using **Google Gemini**
- Markdown report generation
- Scheduling via **cron**
- Multi-language support

### Commands

```bash
$ digest init <name>
$ digest cron <name>
$ digest run <name>
$ digest edit <name>
$ digest rm <name>
$ digest ls
```

## Notes

- Requires a Gemini API key
- Requires an OPML URL as RSS feed source
