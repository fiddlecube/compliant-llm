# Configuration Guide

Compliant LLM uses YAML configuration files to provide a flexible and powerful way to define test scenarios. This guide covers how to create and use configuration files for your prompt testing needs.

## Configuration File Basics

Configuration files are stored in the `configs/` directory by default and use the YAML format. They allow you to specify all aspects of prompt testing, including:

- System prompts to test
- Testing strategies to employ
- Provider settings
- Output options
- Custom test prompts

## File Structure

A basic configuration file includes the following elements:

```yaml
# Basic required settings
prompt: "You are a helpful assistant for a banking organization. Always be professional and courteous."
strategy: prompt_injection,jailbreak

# Provider settings
provider: openai/gpt-4o
temperature: 0.7

# Output settings
output: "report_name"

```

## Required Fields

| Field | Description | Default |
|-------|-------------|---------|
| `prompt` | The system prompt to test | None (Required) |
| `strategy` or `strategies` | Testing strategies to use | None (Required) |

## Optional Fields

| Field | Description | Default |
|-------|-------------|---------|
| `provider` | LLM provider to use | `openai/gpt-4o` [Litellm format] |
| `output` | Path to save the report file | `report_name` |


## Provider Configuration

You can specify different LLM providers for testing:

```yaml
# OpenAI provider
provider: openai/gpt-4o

# Anthropic provider
provider: anthropic/claude-3-opus

# Azure OpenAI provider
provider: azure/gpt-4o
```

## Environment Variables

Compliant LLM uses environment variables for API keys. You should set these before running tests:

```bash
# For OpenAI models
export OPENAI_API_KEY=your-api-key-here

# For Anthropic models
export ANTHROPIC_API_KEY=your-anthropic-key

# For Azure OpenAI models
export AZURE_API_KEY="my-azure-api-key"
export AZURE_API_BASE="https://example-endpoint.openai.azure.com"
export AZURE_API_VERSION="2023-05-15"
```

## Template Variables

Configuration files support template variables, which are useful for reusing common settings:

```yaml
templates:
  base_prompt: "You are a helpful assistant that specializes in {{domain}}."

prompt: "{{base_prompt}} Always respond professionally and accurately."
variables:
  domain: "financial services"
```
