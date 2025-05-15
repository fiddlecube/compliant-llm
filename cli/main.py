"""
CLI entry point for Prompt Secure.

This module serves as the entry point for the Prompt Secure CLI.
It imports the commands from the commands module and registers them with Click.
"""
from cli.commands import cli


def run_cli():
    """Run the Prompt Secure CLI."""
    cli()


if __name__ == "__main__":
    run_cli()