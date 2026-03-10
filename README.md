# TraktIMDbSync

[![PyPI version](https://img.shields.io/pypi/v/traktimdbsync?cacheSeconds=300)](https://pypi.org/project/TraktIMDbSync/)
[![Python](https://img.shields.io/pypi/pyversions/traktimdbsync?cacheSeconds=300)](https://pypi.org/project/TraktIMDbSync/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

TraktIMDbSync syncs Trakt and IMDb watchlists, ratings, reviews, and watch history in both directions with one Python tool.

This project automates the painful parts of keeping both accounts in sync. It pulls structured data from Trakt, exports your IMDb data, compares both sides, and only applies the missing changes instead of blindly overwriting everything.

This repository is a maintained fork focused on reliability, clearer setup, safer error handling, and a better onboarding experience.

Branding note:

- Project name: `TraktIMDbSync`
- Python package name: `TraktIMDbSync`
- Primary module entrypoint: `python -m TraktIMDbSync`
- Legacy CLI alias: `IMDBTraktSyncer`

If you searched for `Trakt IMDb sync`, `IMDb Trakt watchlist sync`, `Trakt ratings sync`, or `IMDb watch history to Trakt`, this is the tool built for that job.

## Quick start

Use `TraktIMDbSync` as the primary package and command name. A legacy `IMDBTraktSyncer` CLI alias is still available for compatibility.

Install:

```bash
python -m pip install TraktIMDbSync
```

Run:

```bash
python -m TraktIMDbSync
```

Setup takes:

- a Trakt API application
- your IMDb login
- your preferred sync options

## Why people use this tool

- Keep Trakt and IMDb in sync without manual re-entry
- Sync watchlists, ratings, reviews, and watch history from either side
- Avoid duplicate writes by comparing both libraries before syncing
- Handle large accounts better with paginated Trakt reads and improved retries
- Reuse saved settings so repeat runs are much easier

## Why this fork

- better Trakt auth recovery when tokens expire
- improved Trakt API handling for larger libraries
- safer IMDb export detection and CSV parsing
- more stable Windows console output during long runs
- resumable sync checkpoints so interrupted runs can continue instead of restarting from zero
- cleaner onboarding and documentation

## Fork comparison

| Area | Original project | This fork |
|---|---|---|
| Trakt token recovery | Basic | Improved recovery and clearer failures |
| Large Trakt libraries | More limited | Better paginated API reads |
| IMDb export handling | More fragile | Safer download detection and parsing |
| Windows console output | Can be rough on some terminals | Cleaner, safer output for long runs |
| Onboarding | Functional | More guided setup and clearer documentation |

## How to help

- Star the repo if it saves you time
- Open issues with steps, logs, and screenshots when something breaks
- Share the project with other Trakt or IMDb users
- Test IMDb layout changes and report what changed
- Contribute fixes, docs, or automation guides

## Why use it

- Sync watchlists, ratings, reviews, and watch history between Trakt and IMDb
- Avoid duplicate work by only syncing missing items
- Keep long-running syncs stable with retry logic and better Trakt token handling
- Use cached Chrome and Chromedriver downloads managed by the app
- Re-run anytime; saved settings make repeat syncs easier

## What it syncs

| Data type | Trakt -> IMDb | IMDb -> Trakt |
|---|---:|---:|
| Watchlist | Yes | Yes |
| Ratings | Yes | Yes |
| Reviews / comments | Yes | Yes |
| Watch history / check-ins | Yes | Yes |

Notes:

- Shows, movies, and episodes are supported.
- Existing items are usually preserved instead of overwritten.
- Some IMDb actions rely on browser automation because IMDb does not provide a public write API for this workflow.
- Long-running sync phases now save checkpoint progress so crashes or cancelled runs can resume later.

## Requirements

- Python `3.6+`
- Internet access to Trakt, IMDb, and Chrome download endpoints
- A Trakt account
- An IMDb account
- A working desktop environment for Selenium/Chrome automation

Python dependencies:

- `selenium>=4.15.2`
- `requests>=2.32.3`

The package installs these automatically when installed with `pip`.

## Installation

```bash
python -m pip install TraktIMDbSync
```

Run the app:

```bash
python -m TraktIMDbSync
```

You can also use the console entrypoint:

```bash
TraktIMDbSync
```

## Quick start tutorial

### 1. Create a Trakt API application

1. Open `https://trakt.tv/oauth/applications`
2. Create a new application
3. Use this redirect URI:

```text
urn:ietf:wg:oauth:2.0:oob
```

4. Copy your Trakt `client ID` and `client secret`

### 2. Run the syncer for the first time

```bash
python -m TraktIMDbSync
```

On first run, the app will ask for:

- Trakt client ID
- Trakt client secret
- Trakt authorization approval
- IMDb username/email/phone
- IMDb password
- Sync preferences

### 3. Choose your sync options

Typical first-run setup:

- Enable watchlist sync
- Enable ratings sync
- Enable watch history sync
- Leave advanced cleanup options off until you verify the results

### 4. Let the initial sync finish

The first run can take a while because the app may need to:

- download Chrome and Chromedriver
- export your IMDb data
- wait for IMDb export generation
- compare large watch histories and rating libraries

For large libraries, a first sync can take several minutes.

## How it works

The sync flow is roughly:

1. Authenticate with Trakt and refresh tokens if needed
2. Launch Chrome through Selenium
3. Sign in to IMDb
4. Pull data from Trakt through the API
5. Generate and download IMDb CSV exports
6. Parse both sides into comparable datasets
7. Resolve outdated or redirected IMDb IDs when needed
8. Compare differences and build action lists
9. Save progress checkpoints during long sync phases
10. Apply only the missing changes to each side, resuming from saved checkpoints if needed

This approach makes the sync safer than a naive full overwrite.

## Resume after interruption

This fork includes resumable sync checkpoints for long runs.

If the app is cancelled, closed, or crashes during a large sync:

- completed items are remembered in `IMDBTraktSyncer/sync_checkpoint.json`
- the next run skips work that already finished in supported phases
- a fully successful run clears the checkpoint file automatically

This is especially useful for very large watch history libraries where a full run can take a long time.

## First-run behavior

The app stores settings and credentials in a local `credentials.txt` file inside the package directory.

Important:

- Credentials are stored locally on disk
- Treat that machine as trusted
- Use a unique IMDb password if possible
- If credentials change, clear them and re-run setup

Find the package directory:

```bash
python -m TraktIMDbSync --directory
```

## Commands

| Command | Description |
|---|---|
| `TraktIMDbSync --help` | Show available CLI options |
| `TraktIMDbSync --directory` | Print the package directory |
| `TraktIMDbSync --clear-user-data` | Remove saved credentials and prompts |
| `TraktIMDbSync --clear-cache` | Remove cached browsers, drivers, and logs |
| `TraktIMDbSync --uninstall` | Clear browser cache before uninstalling |
| `TraktIMDbSync --clean-uninstall` | Remove all cached data and credentials |

## Updating

```bash
python -m pip install TraktIMDbSync --upgrade
```

Install a specific version:

```bash
python -m pip install TraktIMDbSync==VERSION_NUMBER
```

## Manual install from source

1. Clone or download this repository
2. Open a terminal in the project root
3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

4. Run the app

```bash
python -m TraktIMDbSync
```

## Common use cases

### Keep Trakt and IMDb ratings aligned

Enable ratings sync and run the tool periodically.

### Mirror your watchlist both ways

Enable watchlist sync. If you also enable watched-item cleanup, the app can remove watched entries from watchlists.

### Backfill watch history from ratings

Enable the option to mark rated movies and episodes as watched.

### Run scheduled syncs

After the first successful run, automate the command with Task Scheduler, cron, or launchd.

## Troubleshooting

### IMDb login fails

Common causes:

- wrong credentials
- IMDb captcha or anti-bot challenge
- stale browser session

Try this:

1. Sign in to IMDb manually in Chrome on the same machine
2. Complete any captcha or verification step
3. Run the sync again

### Trakt auth fails

If your refresh token becomes invalid, re-run the app and complete Trakt authorization again.

### The sync is slow

This is normal for large accounts. The biggest delays usually come from:

- IMDb export generation
- browser automation on IMDb pages
- first-run browser downloads

### The app seems stuck on IMDb exports

Wait longer before cancelling. IMDb export generation can take several minutes for larger accounts.

### Where are logs stored?

Use:

```bash
python -m TraktIMDbSync --directory
```

Then inspect `log.txt` in that directory.

## Performance and reliability notes

Recent improvements in this fork include:

- better Trakt token recovery
- proactive Trakt token refresh before expiry-related failures
- paginated Trakt reads so large accounts are loaded more completely
- batched Trakt write requests to reduce API chatter and speed up syncs
- more resilient IMDb export detection and parsing
- cached Trakt lookups for IMDb review media types
- resumable sync checkpoints for interrupted long-running jobs
- safer console output on Windows terminals
- fewer false-positive error logs for normal empty-list situations

## Security note

This tool needs account credentials and browser automation to work around IMDb limitations.

Please understand the tradeoffs:

- IMDb automation is inherently more fragile than a real public API
- local credentials should be protected
- use this on a machine you trust

## Project structure

| Path | Purpose |
|---|---|
| `TraktIMDbSync/__main__.py` | Public module entrypoint |
| `IMDBTraktSyncer/IMDBTraktSyncer.py` | Core CLI implementation |
| `IMDBTraktSyncer/traktData.py` | Trakt reads and transformation |
| `IMDBTraktSyncer/imdbData.py` | IMDb export download and parsing |
| `IMDBTraktSyncer/errorHandling.py` | Retry logic, helpers, and recovery |
| `IMDBTraktSyncer/authTrakt.py` | Trakt OAuth handling |
| `IMDBTraktSyncer/verifyCredentials.py` | Stored settings and credential prompts |
| `IMDBTraktSyncer/QUICKSTART.md` | Short setup guide |
| `IMDBTraktSyncer/CHANGELOG.md` | Release history |

## Contributing

Contributions are welcome.

Good ways to help:

- report reproducible bugs with logs and steps
- test layout changes on IMDb pages
- improve sync edge cases for large libraries
- help reduce Selenium fragility
- improve documentation and onboarding

If you open an issue or pull request, include:

- your operating system
- Python version
- what you tried to sync
- whether the failure was on Trakt or IMDb
- relevant lines from `log.txt`

## Roadmap ideas

- more batching for Trakt write operations
- cleaner progress reporting for long syncs
- better scheduled-run guidance
- more resilient IMDb UI fallbacks
- safer secrets handling for advanced users

## Help and support

- Read `IMDBTraktSyncer/QUICKSTART.md` for a faster walkthrough
- Check `IMDBTraktSyncer/CHANGELOG.md` for release notes
- Use the project issue tracker for bugs and feature requests

## License

This project is released under the MIT License. See `LICENSE`.
