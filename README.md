# FC Prompt Tester

A comprehensive tool for testing AI system prompts against various attack vectors and edge cases.

## Overview

FC Prompt Tester helps developers evaluate the robustness of their AI assistant system prompts by testing them against common attack patterns such as prompt injection, jailbreaking, adversarial inputs, and more.

## Features

- Test system prompts against 8+ attack strategies
- Support for advanced configuration via YAML
- Interactive CLI with rich output
- Visual dashboard for result analysis
- Support for multiple LLM providers (via LiteLLM)
- Parallel testing for faster execution
- Detailed reporting and analysis

## Installation

### Using pip

```bash
pip install fc-prompt-tester
```

### From source

```bash
git clone https://github.com/yourusername/fc-prompt-tester.git
cd fc-prompt-tester
pip install -e .
```

## Quick Start

1. Set up your OpenAI API key:

```bash
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

2. Run a basic test:

```bash
fc-test --prompt "You are a helpful assistant" --strategy prompt_injection,jailbreak
```

3. Or use a configuration file:

```bash
fc-test --config configs/enhanced_config.yaml
```

4. View test results in the dashboard:

```bash
fc-ui
```

## CLI Commands

FC Prompt Tester provides several commands:

### Test Command

```bash
fc-test [OPTIONS]
```

Options:
- `--config, -c`: Path to configuration file
- `--prompt, -p`: Direct input of system prompt
- `--strategy, -s`: Comma-separated list of test strategies
- `--provider, -m`: LLM provider to use
- `--parallel, -j`: Run tests in parallel
- `--verbose, -v`: Increase verbosity

### Report Command

```bash
fc-report [REPORT_FILE] [OPTIONS]
```

Options:
- `--format, -f`: Output format (text, json, html)
- `--summary`: Show only summary statistics

### Generate Command

```bash
fc-generate [TYPE] [OPTIONS]
```

Types:
- `config`: Generate a config file template
- `prompt`: Generate sample prompts based on use cases

Options:
- `--template, -t`: Template to use
- `--output, -o`: Output file path

### Config Command

```bash
fc-config [OPTIONS]
```

Options:
- `--list, -l`: List available configurations
- `--show, -s`: Show details for a specific configuration
- `--validate, -v`: Validate a configuration file

## Configuration Format

FC Prompt Tester uses YAML for configuration. Here's an example:

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
docker build -t fc-prompt-tester .
docker run -p 8501:8501 fc-prompt-tester
```

## Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.