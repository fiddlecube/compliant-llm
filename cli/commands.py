#  flake8: noqa : E501
"""
Enhanced CLI commands for Compliant LLM.
"""
import os
import sys
import json
import yaml
import click
import importlib.metadata
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.progress import (
    Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
)
from typing import Dict, Any, Callable
from rich import box
from core.runner import execute_prompt_tests, execute_rerun_test
from core.config_manager.cli_adapter import CLIConfigAdapter
from core.analytics.tracker import analytics_tracker
from core.analytics.tracker import UsageEvent, ErrorEvent, InteractionType


def dict_to_cli_table(
    data: Dict[str, Any], 
    title: str = "Data Table", 
    key_column: str = "Key", 
    value_column: str = "Value", 
    box_style=box.ROUNDED, 
    key_style: str = "cyan", 
    value_style: str = "green", 
    key_formatter: Callable[[str], str] = lambda k: k.capitalize(), 
    max_text_length: int = 50
) -> Table:
    """
    Create a formatted table from any dictionary data.
    
    Args:
        data: Dictionary containing data to display
        title: Title for the table
        box_style: Box style for the table borders
        key_column: Name for the key column
        value_column: Name for the value column
        key_style: Rich style for the key column
        value_style: Rich style for the value column
        key_formatter: Function to format keys before display
        max_text_length: Maximum length for text values before truncation
        
    Returns:
        Rich Table object with formatted data
    """
    # Create table with specified styling
    table = Table(title=title, box=box_style)
    table.add_column(key_column, style=key_style)
    table.add_column(value_column, style=value_style)
    
    # Add all data entries to the table
    for key, value in data.items():
        # Format the value based on its type
        if isinstance(value, list):
            formatted_value = ", ".join(str(item) for item in value) if value else "None"
            if len(formatted_value) > max_text_length:
                formatted_value = f"{formatted_value[:max_text_length]}..."
        elif isinstance(value, dict):
            # For nested dicts like prompt, show a summary
            if "content" in value and isinstance(value["content"], str):
                content = value["content"]
                if len(content) > max_text_length:
                    formatted_value = f"{content[:max_text_length]}..."
                else:
                    formatted_value = content
            else:
                formatted_value = f"<{len(value)} items>"
        elif isinstance(value, bool):
            formatted_value = "✅ " if value else "❌"
        elif value is None:
            formatted_value = "None"
        else:
            # Convert to string and truncate if needed
            str_value = str(value)
            if len(str_value) > max_text_length:
                formatted_value = f"{str_value[:max_text_length]}..."
            else:
                formatted_value = str_value

        # Add the row with formatted key and value
        table.add_row(key_formatter(key), formatted_value)

    return table


@click.group()
@click.version_option(
    importlib.metadata.version('compliant-llm'),
    '--version',
    '-v',
    message='%(prog)s version %(version)s'
)
def cli():
    """Compliant LLM - Test your AI system prompts for vulnerabilities."""
    pass


@click.command()
@click.option('--config_path', '-c', help='Configuration file to use')
@click.option('--prompt', '-p', help='System prompt to test')
@click.option('--strategy', '-s', default=None, help='Test strategy to use (comma-separated for multiple)')
@click.option('--provider', help='LLM provider name (e.g., openai/gpt-4o)')
@click.option('--output', '-o', help='Output file name for results (default: `report`)')
@click.option('--report', '-r', is_flag=True, help='Show detailed report after testing')
@click.option('--parallel/--no-parallel', default=None, help='Run tests in parallel')
@click.option('--verbose', '-v', is_flag=True, help='Show verbose output')
@click.option('--timeout', type=int, default=None, help='Timeout in seconds for LLM requests')
@click.option('--nist-compliance', '-n', help='Enable NIST compliance assessment', is_flag=True)
def test(config_path, prompt, strategy, provider, output, report, parallel, verbose, timeout, nist_compliance):
    """Run tests on your system prompts."""
    # Create a rich console for showing output
    console = Console()

    # Create the CLI adapter for configuration handling
    cli_adapter = CLIConfigAdapter()
    
    try:
        analytics_tracker.track(UsageEvent(name="test", interaction_type=InteractionType.CLI))
        # Load configuration from CLI arguments
        cli_adapter.load_from_cli(
            config_path=config_path,
            prompt=prompt,
            strategy=strategy,
            provider=provider,
            output=output,
            parallel=parallel,
            timeout=timeout
        )

        # Ensure we have a prompt if not provided in config or CLI
        config_dict = cli_adapter.get_runner_config()
        # Display configuration as a table
        console.print("\nRunning tests with the following configuration:")
        console.print(dict_to_cli_table(config_dict))
        console.print("\n")

        if not prompt and not config_dict.get('prompt'):
            user_prompt = click.prompt("Enter system prompt")
            if 'prompt' not in config_dict:
                config_dict['prompt'] = {}
            if isinstance(config_dict.get('prompt'), dict):
                config_dict['prompt']['content'] = user_prompt
            else:
                config_dict['prompt'] = {'content': user_prompt}
            cli_adapter.config_manager.config = config_dict

        # Display additional information if verbose mode is enabled
        if verbose:
            click.echo("Verbose mode enabled")
            click.echo(f"Configuration: {config_dict}")

        # Get the configuration for the runner
        runner_config = cli_adapter.get_runner_config()
        if nist_compliance:
            runner_config['nist_compliance'] = True

    except FileNotFoundError as e:
        click.echo(str(e), err=True)
        analytics_tracker.track(ErrorEvent(name="test", interaction_type=InteractionType.CLI, error_msg=str(e)))
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error processing configuration: {e}", err=True)
        analytics_tracker.track(ErrorEvent(name="test", interaction_type=InteractionType.CLI, error_msg=str(e)))
        sys.exit(1)
    
    # Run the tests with a progress indicator
    console.print("\nRunning tests...")
    
    with Progress(
        SpinnerColumn(),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("[cyan]Testing prompt security", total=None)
        report_data = execute_prompt_tests(config_dict=runner_config)
        progress.update(task, completed=True)
    
    
    console.print("[bold green]Tests completed successfully![/]")
    console.print(f"[bold cyan]Report saved successfully at {report_data['report_metadata']['path']}[/]")
    console.print("\n")

    # Check if data has the new schema with metadata and tests
    if 'metadata' in report_data:
        # New schema
        metadata = report_data['metadata']
        
        # Calculate security metrics
        attack_success_count = metadata.get('success_count', 0)
        test_count = metadata.get('test_count', 0)
        attack_success_rate = (attack_success_count / test_count) * 100 if test_count > 0 else 0
        attack_success_style = ("red" if attack_success_rate >= 50 else
                              "yellow" if attack_success_rate >= 20 else "green")
        
        # Create a dictionary with all the report metrics
        report_metrics = {
            "Total Tests": test_count,
            "Total Security Breaches": f"[{attack_success_style}]{attack_success_count}",
            "Tested Strategies": metadata.get('strategies') or "-",
            "Breached Strategies": metadata.get('breached_strategies') or "-",
            "Successful Mutations": metadata.get('successful_mutation_techniques') or "-",
            "Execution Time": f"{metadata.get('elapsed_seconds', 0):.2f} seconds"
        }
        
        # Create and print the table using the generic function
        report_table = dict_to_cli_table(
            report_metrics,
            title="🔒 Compliant LLM Report Summary",
            key_column="Metric",
            value_column="Value"
        )
        
        # Print the table
        console.print(report_table)
        
        # Print a summary of vulnerabilities found
        if attack_success_count > 0:
            console.print(
                f"\n[bold red]⚠️  {attack_success_count} Vulnerabilities found![/]"
            )
            console.print("[yellow]Review the full report in the Streamlit dashboard:[/]")
            console.print("[blue]Run 'compliant-llm dashboard' to view the report[/]")
        else:
            console.print("\n[bold green]✅ No vulnerabilities found![/]")
    else:
        # Legacy schema
        # Create a new table for report summary
        table = Table(title="🔒 Compliant LLM Report Summary", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Total Tests", f"{len(report_data)}")
        console.print(table)


@click.command()
@click.argument('report_file', required=False, default=None)
@click.option('--format', '-f', type=click.Choice(['text', 'json', 'html']), default='text', help='Output format')  # noqa: E501
@click.option('--summary', '-s', is_flag=True, help='Show only summary statistics')
def report(report_file, format, summary):
    """Analyze and view previous test results. If no file is specified, uses the latest report."""
    analytics_tracker.track(UsageEvent(name="report", interaction_type=InteractionType.CLI))
    try:
        # If no report file is specified, find the latest one
        if not report_file:
            report_dir = "reports"
            if not os.path.exists(report_dir):
                raise FileNotFoundError(f"No reports found in {report_dir}")
                
            # Find all report files
            report_files = [f for f in os.listdir(report_dir) if f.startswith("report_") and f.endswith(".json")]
            if not report_files:
                raise FileNotFoundError(f"No report files found in {report_dir}")
                
            # Sort by timestamp and get the latest one
            latest_file = sorted(report_files)[-1]
            report_file = os.path.join(report_dir, latest_file)
            
        with open(report_file, 'r') as f:
            data = json.load(f)

        if summary:
            # Display summary statistics
            click.echo(f"Report Summary ({report_file}):")
            # Check if data has the new schema with metadata and tests
            if 'metadata' in data and 'tests' in data:
                # New schema
                metadata = data['metadata']
                tests = data['tests']
                click.echo(f"Total tests: {len(tests)}")
                click.echo(f"Provider: {metadata.get('provider', 'Unknown')}")
                click.echo(f"Strategies: {', '.join(metadata.get('strategies', ['Unknown']))}")
                click.echo(f"Success rate: {metadata.get('success_count', 0)}/{metadata.get('test_count', 0)}")
                click.echo(f"Execution time: {metadata.get('elapsed_seconds', 0):.2f} seconds")
            else:
                # Legacy schema
                click.echo(f"Total tests: {len(data)}")
        elif format == 'text':
            # Simple text output
            tests = data.get('tests', data)  # Handle both new and legacy schema
            for i, entry in enumerate(tests):
                click.echo(f"Test {i+1}:")
                if 'prompt' in entry:
                    click.echo(f"  Prompt: {entry['prompt']}")
                if 'result' in entry and 'choices' in entry['result'] and len(entry['result']['choices']) > 0:
                    if 'message' in entry['result']['choices'][0]:
                        content = entry['result']['choices'][0]['message'].get('content', 'No content')
                        click.echo(f"  Response: {content[:100]}..." if len(content) > 100 else f"  Response: {content}")
                click.echo("")
        elif format == 'json':
            # Pretty JSON output
            click.echo(json.dumps(data, indent=2))
        elif format == 'html':
            # Generate HTML report
            html_path = report_file.replace('.json', '.html')
            with open(html_path, 'w') as f:
                f.write("<html><head><title>Compliant LLM Test Report</title></head><body>")
                f.write("<h1>Test Report</h1>")
                # Add more HTML formatting here
                f.write("</body></html>")
            click.echo(f"HTML report saved to {html_path}")

    except FileNotFoundError as e:
        analytics_tracker.track(ErrorEvent(name="report", interaction_type=InteractionType.CLI, error_msg=str(e)))    
        click.echo(f"Error: Report file not found: {e}", err=True)
        sys.exit(1)
    except json.JSONDecodeError:
        analytics_tracker.track(ErrorEvent(name="report", interaction_type=InteractionType.CLI, error_msg="Invalid JSON format in report file."))
        click.echo("Error: Invalid JSON format in report file.", err=True)
        sys.exit(1)


@click.command()
@click.argument('type', type=click.Choice(['config', 'prompt']))
@click.option('--template', '-t', help='Template name to use')
@click.option('--output', '-o', help='Output file path')
def generate(type, template, output):
    """Generate configuration files or sample prompts."""
    if type == 'config':
        # Define some templates
        templates = {
            'basic': {
                'prompt': 'You are a helpful AI assistant.',
                'strategy': 'prompt_injection,jailbreak',
                'provider_name': 'openai/gpt-4o'
            },
            'modern': {
                'name': 'Basic Test',
                'description': 'A basic test configuration',
                'prompt': {
                    'content': 'You are a helpful AI assistant.'
                },
                'strategies': [
                    {'name': 'prompt_injection', 'enabled': True},
                    {'name': 'jailbreak', 'enabled': True}
                ],
                'provider': {
                    'name': 'openai/gpt-4o'
                },
                'output': {
                    'format': 'json',
                    'path': './reports/'
                }
            }
        }

        # Select template
        template_name = template or 'modern'
        if template_name not in templates:
            click.echo(f"Unknown template: {template_name}. Available templates: {', '.join(templates.keys())}", err=True)
            sys.exit(1)

        # Generate config
        config_content = yaml.dump(templates[template_name], default_flow_style=False)

        # Output
        if output:
            with open(output, 'w') as f:
                f.write(config_content)
            click.echo(f"Config written to {output}")
        else:
            click.echo(config_content)
    
    elif type == 'prompt':
        # Define some prompt templates
        prompts = {
            'customer_service': """You are an AI assistant for customer support. Your role is to help users with their product-related inquiries and provide excellent service.

Your responses should be:
  1. Friendly and helpful, creating a positive customer experience.
  2. Clear and to the point, avoiding technical jargon when possible.
  3. Solution-oriented, focusing on resolving the customer's issue.
  4. Empathetic to customer frustrations.""",
            
            'banking': """You are an AI assistant for a banking organization. Your role is to assist users with inquiries related to their banking needs, account information, and financial services.

Your responses should be:
  1. Professional and courteous, reflecting the bank's reputation for excellence in financial services.
  2. Knowledgeable about banking products, services, and general financial information.
  3. Concise yet informative.
  4. Supportive of responsible financial practices."""
        }

        # Select template
        template_name = template or 'customer_service'
        if template_name not in prompts:
            click.echo(f"Unknown prompt template: {template_name}. Available templates: {', '.join(prompts.keys())}", err=True)
            sys.exit(1)

        # Output
        if output:
            with open(output, 'w') as f:
                f.write(prompts[template_name])
            click.echo(f"Prompt written to {output}")
        else:
            click.echo(prompts[template_name])


@click.command()
@click.option('--list', '-l', is_flag=True, help='List available configurations')
@click.option('--show', '-s', help='Show details for a specific configuration')
@click.option('--validate', '-v', help='Validate a configuration file')
def config(list, show, validate):
    """Manage configuration files."""
    if list:
        click.echo("Available configurations:")
        # Get the list of config directories from core.config
        config_dirs = [
            # Package configs
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs"),
            # User configs
            os.path.expanduser(os.path.join("~", ".config", "compliant-llm")),
            # Project configs (current directory)
            os.path.join(os.getcwd(), ".compliant-llm")
        ]
        
        for config_dir in config_dirs:
            if os.path.exists(config_dir):
                click.echo(f"\nIn {config_dir}:")
                configs = [f for f in os.listdir(config_dir) if f.endswith(('.yaml', '.yml'))]  # noqa: E501
                for config_file in configs:
                    click.echo(f"  - {config_file}")
    
    elif show:
        # Create the CLI adapter for configuration handling
        cli_adapter = CLIConfigAdapter()
        
        try:
            # Load from a specified config file
            cli_adapter.load_from_cli(config=show)
            
            # Output the raw configuration
            click.echo(yaml.dump(cli_adapter.config_manager.config, default_flow_style=False))  # noqa: E501
        except FileNotFoundError as e:
            click.echo(str(e), err=True)
            sys.exit(1)
    
    elif validate:
        # Create the CLI adapter for configuration handling
        cli_adapter = CLIConfigAdapter()
        
        try:
            # Load from a specified config file
            cli_adapter.load_from_cli(config=validate)
            
            # Get the runner config (this performs validation)
            runner_config = cli_adapter.get_runner_config()
            
            click.echo(f"Configuration is valid: {validate}")
            click.echo("Processed configuration for runner:")
            click.echo(yaml.dump(runner_config, default_flow_style=False))
        except FileNotFoundError as e:
            click.echo(f"Error: Configuration file not found: {e}", err=True)
            sys.exit(1)
        except Exception as e:
            click.echo(f"Configuration validation failed: {e}", err=True)
            sys.exit(1)
    
    else:
        # Display help if no options provided
        ctx = click.get_current_context()
        click.echo(ctx.get_help())


@click.command()
@click.argument('prompt')
@click.option('--report-file', '-r', default=None, help='Previous report file to rerun')
def rerun(prompt, report_file):
    """Rerun attacks from a previous report with a new system prompt.
    
    This command allows you to reuse the attack strategies from a previous test
    but with a different system prompt. If no report file is specified, the
    most recent report will be used.
    """
    # Create a rich console for showing output
    console = Console()
    analytics_tracker.track(UsageEvent(name="rerun", interaction_type=InteractionType.CLI))
    # Validate inputs
    if not prompt:
        console.print("[red]Error: System prompt is required.[/red]")
        sys.exit(1)
        
    # Read configuration from config.yaml
    cli_adapter = CLIConfigAdapter()
    
    try:
        # Load the default configuration
        cli_adapter.load_from_cli(
            prompt=prompt,
        )
        
        # Get the configuration for the runner
        config_dict = cli_adapter.get_runner_config()

    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        sys.exit(1)
    
    # Generate timestamp for report file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create output directory if it doesn't exist
    output_dir = "reports"
    os.makedirs(output_dir, exist_ok=True)
    
    # Set output file path if not specified
    output_filename = f"rerun_report_{timestamp}.json"
    output = os.path.join(output_dir, output_filename)
    
    # Create and configure orchestrator
    # Run the rerun with a progress indicator
    console.print(f"\n[bold green]Rerunning attacks with new system prompt:[/] '{prompt}'")
    
    try:
        # Execute rerun with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("[cyan]Rerunning security tests", total=None)
            
            # Run the attacks against new system prompt using same strategies
            # This uses the default asyncio implementation from runner.py
            report_data = execute_rerun_test(config_dict, report_file)
            
            progress.update(task, completed=True)

        console.print("[bold green]Rerun completed successfully![/]")
        console.print(f"[bold cyan]Report saved to: {report_data['report_metadata']['path']}[/]")
        console.print("\n")
        
        # Display summary
        # Check if data has the new schema with metadata and tests
        if 'metadata' in report_data:
            # New schema
            metadata = report_data['metadata']
            
            # Calculate security metrics
            attack_success_count = metadata.get('success_count', 0)
            test_count = metadata.get('test_count', 0)
            attack_success_rate = (attack_success_count / test_count) * 100 if test_count > 0 else 0
            attack_success_style = ("red" if attack_success_rate >= 50 else
                                "yellow" if attack_success_rate >= 20 else "green")
            
            # Create a dictionary with all the report metrics
            report_metrics = {
                "Total Tests": test_count,
                "Total Security Breaches": f"[{attack_success_style}]{attack_success_count}",
                "Tested Strategies": (metadata.get('strategies')) or "-",
                "Breached Strategies": metadata.get('breached_strategies') or "-",
                "Successful Mutations": metadata.get('successful_mutation_techniques') or "-",
                "Execution Time": f"{metadata.get('elapsed_seconds', 0):.2f} seconds"
            }
            
            # Create and print the table using the generic function
            report_table = dict_to_cli_table(
                report_metrics,
                title="🔒 Compliant LLM Report Summary",
                key_column="Metric",
                value_column="Value"
            )
            
            # Print the table
            console.print(report_table)
            
            # Print a summary of vulnerabilities found
            if attack_success_count > 0:
                console.print(
                    f"\n[bold red]⚠️  {attack_success_count} Vulnerabilities found![/]"
                )
                console.print("[yellow]Review the full report for details.[/]")
            else:
                console.print("\n[bold green]✅ No vulnerabilities found![/]")
        else:
            # Legacy schema
            # Create a new table for report summary
            table = Table(title="Compliant LLM Report Summary", box=box.ROUNDED)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            table.add_row("Total Tests", f"{len(report_data)}")
            console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error during rerun: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)
        
if __name__ == '__main__':
    cli()
