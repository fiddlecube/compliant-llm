import click
import yaml
from core.runner import run_tests

@click.command()
@click.option('--config', type=click.Path(), help='Path to YAML config')
def run_cli(config):
    if config:
        with open(config) as f:
            cfg = yaml.safe_load(f)
        run_tests({ 'prompt': cfg['prompt'], 'strategy': cfg['strategy'], 'provider_name': cfg['provider_name']})
    else:
        prompt = input("Enter system prompt: ")
        run_tests({'prompt': prompt, 'strategy': 'prompt_injection', 'provider_name': 'openai/gpt-4o'})

if __name__ == "__main__":
    run_cli()