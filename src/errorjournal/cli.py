import typer
import subprocess
import sys
import os
import shlex
import time
from datetime import datetime

from errorjournal.db import insert_run, recent_runs

app = typer.Typer()

def guess_target_file(args: list[str]) -> str | None:
    """Finds the first argument that is an existing file"""
    for arg in args:
        if not arg.startswith("-") and os.path.isfile(arg):
            return os.path.abspath(arg)
    return None

@app.command("run", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def main_command(ctx: typer.Context):
    """Runs the command and saves the result in database."""
    program_args = ctx.args

    if not program_args:
        print("Error: No command provided to ej.", file=sys.stderr)
        raise typer.Exit(code=1)

    captured_errors = []

    started_at = datetime.now().astimezone().isoformat()
    command_str = shlex.join(program_args)
    target_file = guess_target_file(program_args)

    start_time = time.monotonic()
    return_code = 0

    try:
        with subprocess.Popen(
            program_args,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            errors="replace",
            shell=False
        ) as proc:
            if proc.stderr:
                for line in proc.stderr:
                    sys.stderr.write(line)
                    sys.stderr.flush()
                    captured_errors.append(line)
            return_code = proc.wait()

    except KeyboardInterrupt:
        return_code = 130
        sys.stderr.write("\nProcess interrupted by user.\n")
        sys.stderr.flush()
    
    except FileNotFoundError:
        print(f"Error: Command '{program_args[0]}' not found.", file=sys.stderr)
        return_code = 127

    finally:
        end_time = time.monotonic()
        duration_ms = int((end_time - start_time) * 1000)
        full_error_log = "".join(captured_errors)

        insert_run(
            started_at=started_at,
            command=command_str,
            target_file=target_file,
            exit_code=return_code,
            duration_ms=duration_ms,
            stderr=full_error_log
        )

    raise typer.Exit(code=return_code)

@app.command("log")
def log_command(limit: int = typer.Option(20, "--limit", "-n", help="Number of records to display")):
    """Displays a list of recent runs from the database."""
    runs = recent_runs(limit)
    
    if not runs:
        print("No runs yet.")
        return

    for run in runs:
        dt = datetime.fromisoformat(run["started_at"])
        formatted_time = dt.strftime("%m-%d %H:%M")
        
        status = "OK " if run["exit_code"] == 0 else "ERR"
        duration_str = f"{run['duration_ms']}ms"
        print(f"{run['id']:>4}  {formatted_time}  {status}  {duration_str:>7}  {run['command']}")

def main():
    known_subcommands = {"run", "log"}

    args = sys.argv[1:]

    if args and args[0] not in known_subcommands and not args[0].startswith("-"):
        sys.argv.insert(1, "run")

    app()

if __name__ == "__main__":
    main()