# Quick Start Guide

This guide will help you get up and running with Compliant LLM quickly.

## Prerequisites

- Python 9 or higher
- An API key for at least one of the supported LLM providers (OpenAI, Anthropic, Google)

## Installation

If you haven't installed Compliant LLM yet, follow the [installation instructions](installation.md).

## Basic Usage

### 1. Set up your API key

```bash
# For OpenAI models (recommended for first-time users)
export OPENAI_API_KEY=your-api-key-here
```

### 2. Run a simple test

Test a basic system prompt against prompt injection attacks:

```bash
compliant-llm test --prompt "You are a helpful assistant for a banking organization." --verbose
```

This will:

- Test your prompt against the default prompt injection strategy
- Use the OpenAI GPT-4o model
- Save results to `reports/report.json`
- Display verbose output during testing

### 3. View the test report

```bash
compliant-llm report --summary
```

This will show a summary of your test results, including:
- Number of successful/failed tests
- Timestamp and settings used for the test

### 4. Run tests with multiple strategies

```bash
compliant-llm test --prompt "You are a helpful assistant." \
  --strategy prompt_injection,jailbreak,adversarial
```

### 5. Create and use a configuration file

For more complex testing scenarios, create a configuration file:

```bash
compliant-llm generate config --output configs/my_config.yaml
```

Edit the generated file according to your needs, then run tests using this configuration:

```bash
compliant-llm test --config configs/my_config.yaml
```

## Next Steps

- Explore the [CLI Documentation](cli/commands.py) for all available commands and options
- Learn about [configuration options](configuration.md) for advanced testing scenarios
