"""
Enhanced CLI commands for FC Prompt Tester.
"""
import os
import sys
import json
import yaml
import click
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from core.enhanced_runner import run_tests

# Constants
CONFIG_DIRS = [
    # Package configs
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs"),
    # User configs
    os.path.expanduser(os.path.join("~", ".config", "fc-prompt-tester")),
    # Project configs (current directory)
    os.path.join(os.getcwd(), ".fc-prompt-tester")
]


def find_config_file(config_name: str) -> Optional[str]:
    """Find a config file across various possible locations."""
    # If it's an absolute path or exists in current directory
    if os.path.isabs(config_name) or os.path.exists(config_name):
        return config_name
    
    # Check standard config locations
    for config_dir in CONFIG_DIRS:
        config_path = os.path.join(config_dir, config_name)
        if os.path.exists(config_path):
            return config_path
        
        # Try with .yaml extension if not provided
        if not config_name.endswith(('.yaml', '.yml')):
            yaml_path = f"{config_path}.yaml"
            if os.path.exists(yaml_path):
                return yaml_path
    
    return None


def load_config(config_path: str) -> Dict[str, Any]:
    """Load and parse a YAML config file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        click.echo(f"Error loading config file: {e}", err=True)
        sys.exit(1)


def resolve_config(config_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process and normalize the config dictionary.
    Handles any transformations needed to make the config compatible with the runner.
    """
    # Initialize with defaults
    processed_config = {
        'prompt': '',
        'strategy': 'prompt_injection',
        'provider_name': 'openai/gpt-4o'
    }
    
    # Extract prompt from modern config format
    if 'prompt' in config_dict:
        if isinstance(config_dict['prompt'], dict):
            if 'content' in config_dict['prompt']:
                processed_config['prompt'] = config_dict['prompt']['content']
            elif 'file' in config_dict['prompt']:
                prompt_file = config_dict['prompt']['file']
                try:
                    with open(prompt_file, 'r') as f:
                        processed_config['prompt'] = f.read()
                except Exception as e:
                    click.echo(f"Error reading prompt file {prompt_file}: {e}", err=True)
                    sys.exit(1)
        else:
            # Direct prompt string
            processed_config['prompt'] = config_dict['prompt']
    
    # Extract strategies
    if 'strategies' in config_dict:
        # Modern format with strategy objects
        enabled_strategies = []
        for strategy in config_dict['strategies']:
            if isinstance(strategy, dict) and strategy.get('enabled', True):
                enabled_strategies.append(strategy['name'])
            elif isinstance(strategy, str):
                enabled_strategies.append(strategy)
        
        if enabled_strategies:
            processed_config['strategy'] = ','.join(enabled_strategies)
    elif 'strategy' in config_dict:
        # Legacy format with comma-separated string
        processed_config['strategy'] = config_dict['strategy']
    
    # Extract provider name
    if 'provider' in config_dict:
        if isinstance(config_dict['provider'], dict):
            if 'name' in config_dict['provider']:
                processed_config['provider_name'] = config_dict['provider']['name']
        else:
            processed_config['provider_name'] = config_dict['provider']
    elif 'provider_name' in config_dict:
        processed_config['provider_name'] = config_dict['provider_name']
    
    return processed_config


@click.group()
def cli():
    """FC Prompt Tester - Test your AI system prompts for vulnerabilities."""
    pass


@cli.command()
@click.option('--config', '-c', type=click.Path(exists=False), help='Path to YAML config file')
@click.option('--prompt', '-p', help='Direct input of system prompt')
@click.option('--strategy', '-s', help='Comma-separated list of test strategies')
@click.option('--provider', '-m', help='LLM provider to use')
@click.option('--output', '-o', help='Output format (json, csv, html)')
@click.option('--report', '-r', is_flag=True, help='Generate detailed report')
@click.option('--parallel', '-j', is_flag=True, help='Run tests in parallel')
@click.option('--verbose', '-v', is_flag=True, help='Increase verbosity')
@click.option('--timeout', type=int, default=30, help='Timeout for LLM API calls (seconds)')
@click.option('--save', help='Save results to custom location')
def test(config, prompt, strategy, provider, output, report, parallel, verbose, timeout, save):
    """Run tests on your system prompts."""
    # Initialize configuration
    test_config = {
        'prompt': '',
        'strategy': 'prompt_injection',
        'provider_name': 'openai/gpt-4o'
    }
    
    # Load from config file if specified
    if config:
        config_path = find_config_file(config)
        if not config_path:
            click.echo(f"Config file not found: {config}", err=True)
            sys.exit(1)
        
        click.echo(f"Loading config from: {config_path}")
        config_dict = load_config(config_path)
        test_config = resolve_config(config_dict)
    
    # Override with command line arguments if provided
    if prompt:
        test_config['prompt'] = prompt
    if strategy:
        test_config['strategy'] = strategy
    if provider:
        test_config['provider_name'] = provider
    
    # Ensure we have a prompt
    if not test_config['prompt']:
        if not config:  # Only prompt if not using a config file
            test_config['prompt'] = click.prompt("Enter system prompt")
    
    # Additional options
    if verbose:
        click.echo("Verbose mode enabled")
        click.echo(f"Configuration: {test_config}")
    
    # Run the tests
    run_tests(test_config)
    
    click.echo("Tests completed successfully!")


@cli.command()
@click.argument('report_file', required=False, default='report.json')
@click.option('--format', '-f', type=click.Choice(['text', 'json', 'html']), default='text', help='Output format')
@click.option('--summary', is_flag=True, help='Show only summary statistics')
def report(report_file, format, summary):
    """Analyze and view previous test results."""
    try:
        with open(report_file, 'r') as f:
            data = json.load(f)
        
        if summary:
            # Display summary statistics
            click.echo(f"Report Summary ({report_file}):")
            click.echo(f"Total tests: {len(data)}")
            # Add more summary stats here
        elif format == 'text':
            # Simple text output
            for i, entry in enumerate(data):
                click.echo(f"Test {i+1}:")
                click.echo(f"  Prompt: {entry['prompt']}")
                click.echo(f"  Response: {entry['result']['choices'][0]['message']['content'][:100]}...")
                click.echo("")
        elif format == 'json':
            # Pretty JSON output
            click.echo(json.dumps(data, indent=2))
        elif format == 'html':
            # Generate HTML report
            html_path = report_file.replace('.json', '.html')
            with open(html_path, 'w') as f:
                f.write("<html><head><title>FC Prompt Test Report</title></head><body>")
                f.write(f"<h1>Test Report</h1>")
                # Add more HTML formatting here
                f.write("</body></html>")
            click.echo(f"HTML report saved to {html_path}")
    
    except FileNotFoundError:
        click.echo(f"Report file not found: {report_file}", err=True)
        sys.exit(1)
    except json.JSONDecodeError:
        click.echo(f"Invalid JSON in report file: {report_file}", err=True)
        sys.exit(1)


@cli.command()
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


@cli.command()
@click.option('--list', '-l', is_flag=True, help='List available configurations')
@click.option('--show', '-s', help='Show details for a specific configuration')
@click.option('--validate', '-v', help='Validate a configuration file')
def config(list, show, validate):
    """Manage configuration files."""
    if list:
        click.echo("Available configurations:")
        for config_dir in CONFIG_DIRS:
            if os.path.exists(config_dir):
                click.echo(f"\nIn {config_dir}:")
                configs = [f for f in os.listdir(config_dir) if f.endswith(('.yaml', '.yml'))]
                for config_file in configs:
                    click.echo(f"  - {config_file}")
    
    elif show:
        config_path = find_config_file(show)
        if not config_path:
            click.echo(f"Config file not found: {show}", err=True)
            sys.exit(1)
        
        config_dict = load_config(config_path)
        click.echo(yaml.dump(config_dict, default_flow_style=False))
    
    elif validate:
        config_path = find_config_file(validate)
        if not config_path:
            click.echo(f"Config file not found: {validate}", err=True)
            sys.exit(1)
        
        try:
            config_dict = load_config(config_path)
            # Apply basic validation
            processed = resolve_config(config_dict)
            click.echo(f"Configuration is valid: {config_path}")
            click.echo("Resolved configuration:")
            click.echo(yaml.dump(processed, default_flow_style=False))
        except Exception as e:
            click.echo(f"Configuration validation failed: {e}", err=True)
            sys.exit(1)
    
    else:
        # Display help if no options provided
        ctx = click.get_current_context()
        click.echo(ctx.get_help())


if __name__ == '__main__':
    cli()
