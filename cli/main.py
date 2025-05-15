"""
CLI entry point for Prompt Secure.

This module serves as the entry point for the Prompt Secure CLI.
It imports the commands from the commands module and registers them with Click.
"""
from cli.commands import cli


def run_cli():
    """Run the Prompt Secure CLI."""
    cli()

@cli.command()
def dashboard():
    """Launch Streamlit dashboard for prompt security reports"""
    import subprocess
    import sys
    import os

    # Get the absolute path to the dashboard.py file
    dashboard_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        'ui', 
        'dashboard.py'
    )
    
    subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard_path])


if __name__ == "__main__":
    run_cli()