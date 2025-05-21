# Compliant LLM

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
python -m cli.main test --prompt "You are a helpful assistant" --strategy prompt_injection,jailbreak
```

2. View the report generated:

```bash
python -m cli.main report --summary
```

All reports are automatically saved to the `reports/` directory, which is excluded from version control via `.gitignore`.


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
python -m cli.main test [OPTIONS]
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
python -m cli.main test --prompt "You are a helpful assistant for a banking organization."

# Test with multiple strategies
python -m cli.main test --prompt "You are a helpful assistant." --strategy prompt_injection,jailbreak,adversarial

# Test with a specific provider and custom output path
python -m cli.main test --config configs/config.yaml --provider openai/gpt-3.5-turbo --output reports/custom_report.json

# Run tests in parallel with increased verbosity
python -m cli.main test --config configs/config.yaml --parallel --verbose
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
