# Generate Command

The `generate` command creates template files for configurations and prompts to help you get started quickly with Prompt Secure.

## Synopsis

```bash
python -m cli.main generate [TYPE] [OPTIONS]
```

## Description

The generate command helps you create starter templates for configurations and system prompts. This is particularly useful when you're first getting started with Prompt Secure or when you want to create a new configuration based on a predefined template.

## Arguments

| Argument | Description |
|----------|-------------|
| `TYPE` | The type of template to generate (`config` or `prompt`) |

## Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--template` | `-t` | Template to use | `basic` |
| `--output` | `-o` | Output file path | `generated_config.yaml` or `generated_prompt.txt` |

## Template Types

### Config Templates

When generating configuration templates (`TYPE=config`), the following templates are available:

| Template | Description |
|----------|-------------|
| `basic` | A simple configuration with essential settings |
| `advanced` | A comprehensive configuration with all available options |
| `banking` | A configuration tailored for testing banking/financial assistants |
| `education` | A configuration for educational AI assistants |
| `healthcare` | A configuration for healthcare-related AI assistants |

### Prompt Templates

When generating prompt templates (`TYPE=prompt`), the following templates are available:

| Template | Description |
|----------|-------------|
| `basic` | A general-purpose assistant prompt |
| `banking` | A banking/financial assistant prompt |
| `education` | An educational assistant prompt |
| `healthcare` | A healthcare assistant prompt |
| `customer_service` | A customer service assistant prompt |

## Examples

### Generate a Basic Configuration

Create a basic configuration template:

```bash
python -m cli.main generate config --output configs/my_config.yaml
```

### Generate an Advanced Configuration

Create a more comprehensive configuration template:

```bash
python -m cli.main generate config --template advanced --output configs/advanced_config.yaml
```

### Generate a Domain-Specific Configuration

Create a domain-specific configuration template:

```bash
python -m cli.main generate config --template banking --output configs/banking_config.yaml
```

### Generate a System Prompt

Create a sample system prompt based on a template:

```bash
python -m cli.main generate prompt --template banking --output prompts/banking_prompt.txt
```

## Generated Files

### Configuration File Structure

Generated configuration files use YAML format and follow this structure:

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

### Prompt File Structure

Generated prompt files contain sample system prompts with appropriate guidelines and constraints for the specific domain.

## See Also

- [Test Command](test.md) - For testing prompts
- [Configuration Guide](../configuration/index.md) - For detailed configuration information
