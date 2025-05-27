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

# For Anthropic models
export ANTHROPIC_API_KEY=your-anthropic-key

# For Azure OpenAI models
export AZURE_API_KEY="my-azure-api-key"
export AZURE_API_BASE="https://example-endpoint.openai.azure.com"
export AZURE_API_VERSION="2023-05-15"
```

### 2. Run a simple test

Test a basic system prompt against prompt injection attacks:

```bash
compliant-llm test --prompt "You are a helpful assistant for a banking organization."
```

This will:

- Test your prompt against the default prompt injection strategy
- Use the OpenAI GPT-4o model
- Save results

### 3. View the test report on the UI dashboard

```bash
compliant-llm dashboard
```

![Dashboard View](docs/images/ui_screenshot.png)

Here you will be able to see all your past test runs.

Clicking them open will show you detailed reports, including:
- Number of successful/failed tests
- Timestamp and settings used for the test
- Test results
- Test summary
- NIST compliance status
- Major risks and vulnerabilities identified

You can also start a new test run using the UI.

### 4. Run tests with multiple strategies

```bash
compliant-llm test --prompt "You are a helpful assistant." \
  --strategy "prompt_injection,jailbreak,adversarial"
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

- Learn about [configuration options](configuration.md) for advanced testing scenarios
