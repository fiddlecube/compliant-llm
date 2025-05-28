"""
CLI entry point for Compliant LLM.

This module serves as the entry point for the Compliant LLM CLI.
It imports the commands from the commands module and registers them with Click.
"""
import click
import importlib.metadata
from cli.commands import cli, test, report, config, generate, rerun


def main():
    """Main entry point for the Compliant LLM CLI."""
    # Create the main command group
    @click.group()
    @click.version_option(
        importlib.metadata.version('compliant-llm'),
        '--version',
        '-v',
        message='%(prog)s version %(version)s'
    )
    def compliant_llm():
        """Compliant LLM - Test your AI system prompts for vulnerabilities."""
        pass
    
    # Add subcommands
    compliant_llm.add_command(test)
    compliant_llm.add_command(report)
    compliant_llm.add_command(config)
    compliant_llm.add_command(generate)
    compliant_llm.add_command(dashboard)
    compliant_llm.add_command(rerun)
    
    # Run the CLI
    compliant_llm()


def run_cli():
    """Legacy entry point for backward compatibility."""
    cli()

@click.command()
def run_app():
    """Launch Streamlit dashboard"""
    import subprocess
    import sys
    import os

    # Get the absolute path to the dashboard.py file
    dashboard_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        'ui', 
        'app.py'
    )
    
    # Start Streamlit with specific route
    subprocess.Popen([sys.executable, "-m", "streamlit", "run", dashboard_path, "--server.port", "8502", "--server.baseUrlPath", "/report"])

@cli.command()
def dashboard():
    """Launch Streamlit for running app"""
    import subprocess
    import sys
    import os

    # Get the absolute path to the app.py file
    app_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ui', 'dashboard.py')
    
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