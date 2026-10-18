# Error Journal
A small CLI that wraps your commands, logs every run and (soon) shows you which mistakes you make most often.

## Install
```bash
git clone <this-repo-url>
cd error-journal
python -m venv venv
source venv/Scripts/activate   # Git Bash on Windows; use venv/bin/activate on macOS/Linux
pip install -e .
```

Requires Python 3.10 or newer.

## Usage
Run any command through `ej` and it behaves exactly as normal while logging the result.

```bash
ej python hw.py            # run a command and log it
ej run python hw.py        # same thing, explicit (use this if your program is named "log")
ej log                     # show recent runs
ej log -n 5                # show the last 5 runs
```

Your run history is stored locally in `~/.errorjournal/journal.db`. Set the `EJ_DB` environment variable to use a different file.

## Status
Early development. Currently logs runs, exit codes, durations, and stderr. Error parsing and stats are coming.