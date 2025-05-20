# Compliant LLM

A comprehensive tool for testing AI system prompts against various attack vectors and edge cases.

## Overview

Compliant LLM helps developers evaluate the robustness of their AI assistant system prompts by testing them against common attack patterns such as prompt injection, jailbreaking, adversarial inputs, and more.

## Features

- Test agents against 8+ attack strategies
- Support for advanced configuration via YAML
- Interactive CLI with rich output
- Visual dashboard for result analysis
- Support for multiple LLM providers (via LiteLLM)
- Parallel testing for faster execution
- Detailed reporting and analysis

## Requirements

- Python 3.9+
- pip (Python package installer)
- Access to at least one LLM provider API (OpenAI, Anthropic, or Google)

## Installation

### Using pip

```bash
pip install compliant-llm
```

### From source

```bash
git clone https://github.com/fiddlecube/compliant-llm.git
cd compliant-llm
pip install -e .
```

### Setting Up the Environment

1. Make sure you have Python 3.9 or newer installed:

```bash
python --version
```

2. Create and activate a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Set up environment variables for your API keys:

```bash
# Create a .env file in the project root
echo "OPENAI_API_KEY=your-api-key-here" > .env
echo "ANTHROPIC_API_KEY=your-api-key-here" >> .env
```

## Quick Start

1. Run a basic red-teaming test:

```bash
python -m cli.commands test --prompt "You are a helpful assistant" --strategy prompt_injection,jailbreak
```

2. Or use a configuration file:

```bash
python -m cli.commands test --config configs/config.yaml
```

3. View the test report:

```bash
python -m cli.commands report --summary
```

All reports are automatically saved to the `reports/` directory, which is excluded from version control via `.gitignore`.

## CLI Documentation

Compliant LLM provides a comprehensive command-line interface for testing and evaluating AI system prompts against various attack vectors.
More details in documentation folder.

## Development

### Development Installation

```bash
git clone https://github.com/fiddlecube/compliant-llm.git
cd compliant-llm

pip install -r requirements.txt

```

### Environment Setup

Before using the CLI, set up the necessary API keys as environment variables:

```bash
# For OpenAI models
export OPENAI_API_KEY=your-api-key-here

# For other providers (if needed)
export ANTHROPIC_API_KEY=your-anthropic-key
export GOOGLE_API_KEY=your-google-key
```

You can also create a `.env` file in your project root with these variables.

### File Structure

- **Reports**: All generated reports are saved to the `reports/` directory by default (excluded from git)
- **Configs**: Configuration files are stored in the `configs/` directory
- **Templates**: Template files for generating configs/prompts are in the `templates/` directory

### Test Command

The test command runs prompt tests against specified strategies.

```bash
python -m cli.commands test [OPTIONS]
```

#### Options

| Option | Short | Description | Default |
|--------|-------|-------------|--------|
| `--config` | `-c` | Path to configuration file | None |
| `--prompt` | `-p` | Direct input of system prompt | None |
| `--strategy` | `-s` | Comma-separated list of test strategies | `prompt_injection` |
| `--provider` | `-m` | LLM provider to use | `openai/gpt-4o` |
| `--output` | `-o` | Output file path | `reports/report.json` |
| `--parallel` | `-j` | Run tests in parallel | False |
| `--verbose` | `-v` | Increase verbosity | False |
| `--timeout` | None | Timeout for LLM API calls in seconds | 30 |
| `--temperature` | None | Temperature for LLM API calls | 0.7 |

#### Available Testing Strategies

- `prompt_injection`: Tests resilience against prompt injection attacks
- `jailbreak`: Tests against jailbreak attempts to bypass restrictions
- `system_prompt_extraction`: Tests if the system prompt can be extracted
- `adversarial`: Tests against adversarial inputs
- `stress_test`: Tests system prompt under high pressure scenarios
- `boundary_testing`: Tests boundary conditions of the system prompt
- `context_manipulation`: Tests against context manipulation attacks

#### Examples

```bash
# Basic test with default settings
python -m cli.commands test --prompt "You are a helpful assistant for a banking organization."

# Test with multiple strategies
python -m cli.commands test --prompt "You are a helpful assistant." --strategy prompt_injection,jailbreak,adversarial

# Test with a specific provider and custom output path
python -m cli.commands test --config configs/config.yaml --provider openai/gpt-3.5-turbo --output reports/custom_report.json

# Run tests in parallel with increased verbosity
python -m cli.commands test --config configs/config.yaml --parallel --verbose
```

### Report Command

The report command displays and analyzes test results.

```bash
python -m cli.commands report [REPORT_FILE] [OPTIONS]
```

By default, report files are saved to and read from the `reports/` directory.

#### Options

| Option | Short | Description | Default |
|--------|-------|-------------|--------|
| `--format` | `-f` | Output format (text, json, html) | `text` |
| `--summary` | None | Show only summary statistics | False |

#### Examples

```bash
# View default report in text format
python -m cli.commands report

# View a specific report with summary statistics
python -m cli.commands report reports/custom_report.json --summary

# Export report in JSON format
python -m cli.commands report --format json > analysis.json
```

### Streamlit Dashboard

Visualize your prompt security reports with an interactive dashboard:

```bash
# Launch dashboard
python -m cli.main dashboard


### Generate Command

The generate command creates templates for configurations or prompts.

```bash
python -m cli.commands generate [TYPE] [OPTIONS]
```

#### Types

- `config`: Generate a configuration file template
- `prompt`: Generate sample prompts based on use cases

#### Options

| Option | Short | Description | Default |
|--------|-------|-------------|--------|
| `--template` | `-t` | Template to use | `basic` |
| `--output` | `-o` | Output file path | `generated_config.yaml` or `generated_prompt.txt` |

#### Examples

```bash
# Generate a basic configuration template
python -m cli.commands generate config --output configs/my_config.yaml

# Generate a banking-related prompt example
python -m cli.commands generate prompt --template banking --output prompts/bank_prompt.txt
```

### Config Command

The config command manages and validates configuration files.

```bash
python -m cli.commands config [OPTIONS]
```

#### Options

| Option | Short | Description | Default |
|--------|-------|-------------|--------|
| `--list` | `-l` | List available configurations | None |
| `--show` | `-s` | Show details for a specific configuration | None |
| `--validate` | `-v` | Validate a configuration file | None |

#### Examples

```bash
# List all available configuration files
python -m cli.commands config --list

# Show details for a specific configuration
python -m cli.commands config --show configs/enhanced_config.yaml

# Validate a configuration file
python -m cli.commands config --validate configs/my_config.yaml
```

### Advanced Usage

#### Configuration File Format

Configuration files use YAML format and support the following structure:

```yaml
# Basic configuration
prompt: "You are a helpful assistant..."
strategy: prompt_injection,jailbreak
provider: openai/gpt-4o
output_path: reports/custom_report.json

# Advanced configuration
max_threads: 4
timeout: 30
temperature: 0.7

# Strategy-specific configurations
strategies_config:
  prompt_injection:
    custom_prompts:
      - "Ignore previous instructions..."
```

#### Best Practices

1. **Use Configuration Files**: For complex testing scenarios, use YAML config files instead of command-line arguments
2. **Organize Reports**: Use descriptive filenames for reports to organize test results
3. **Parallel Testing**: For large test suites, use the `--parallel` flag to speed up execution
4. **Provider Selection**: Test against multiple providers to evaluate prompt performance across different models
5. **Regular Testing**: Incorporate prompt testing into your development workflow to catch vulnerabilities early

## Configuration Format

Compliant LLM uses YAML for configuration. Here's an example:

```yaml
name: "System Prompt Test"
description: "Testing a banking assistant prompt"

prompt:
  content: |
    You are an AI assistant for a banking organization...
  variables:
    bank_name: "ACME Bank"

strategies:
  - name: prompt_injection
    enabled: true
  - name: jailbreak
    enabled: true

provider:
  name: openai/gpt-4o
  timeout: 30

output:
  format: json
  path: "./reports/"
```

## Docker

```bash
docker build -t compliant_llm .
docker run -p 8501:8501 compliant_llm
```

## Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
