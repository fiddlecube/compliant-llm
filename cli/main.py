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
    """Launch Streamlit dashboard"""
    import subprocess
    import sys
    import os

    # Get the absolute path to the dashboard.py file
    dashboard_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        'ui', 
        'dashboard.py'
    )
    
    # Start Streamlit with specific route
    subprocess.Popen([sys.executable, "-m", "streamlit", "run", dashboard_path, "--server.port", "8502", "--server.baseUrlPath", "/report"])

@cli.command()
def run_app():
    """Launch Streamlit for running app"""
    import subprocess
    import sys
    import os

    # Get the absolute path to the app.py file
    app_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ui', 'app.py')
    
    # Start Streamlit with app
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        app_path,
        "--server.port",
        "8501"
    ])

if __name__ == "__main__":
    run_cli()