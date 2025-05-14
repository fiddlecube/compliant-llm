"""
CLI entry point for FC Prompt Tester.

This module serves as the entry point for the FC Prompt Tester CLI.
It imports the commands from the commands module and registers them with Click.
"""
from cli.commands import cli


def run_cli():
    """Run the FC Prompt Tester CLI."""
    cli()


if __name__ == "__main__":
    run_cli()