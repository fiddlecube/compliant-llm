# Config Command

The `config` command helps you manage and validate configuration files for Compliant LLM.

## Synopsis

```bash
python -m cli.main config [OPTIONS]
```

## Description

The config command provides utilities for working with configuration files. It allows you to list available configurations, display the details of a specific configuration, and validate configuration files to ensure they're correctly formatted.

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--list` | `-l` | List available configurations |
| `--show` | `-s` | Show details for a specific configuration |
| `--validate` | `-v` | Validate a configuration file |

## Common Use Cases

### Listing Available Configurations

To see all available configuration files in the `configs/` directory:

```bash
python -m cli.main config --list
```

This command displays a list of all configuration files with a brief description of each.

### Viewing Configuration Details

To view the details of a specific configuration file:

```bash
python -m cli.main config --show configs/config.yaml
```

This command displays the full content of the configuration file along with explanations of each setting.

### Validating Configuration Files

To validate a configuration file to ensure it's correctly formatted:

```bash
python -m cli.main config --validate configs/my_config.yaml
```

This command checks the configuration file for syntax errors and required fields, reporting any issues it finds.

## Configuration Structure

Compliant LLM configuration files use YAML format and must include at least the following fields:

- `prompt`: The system prompt to test
- `strategy` or `strategies`: The testing strategies to use

Additional optional fields include:

- `provider`: The LLM provider to use (default: `openai/gpt-4o`)
- `output_path`: Path to save the report file (default: `reports/report.json`)
- `max_threads`: Maximum number of threads to use for parallel testing
- `timeout`: Timeout for LLM API calls in seconds
- `temperature`: Temperature for LLM API calls
- `strategies_config`: Custom settings for specific testing strategies

## Examples

### List All Configurations

```bash
python -m cli.main config --list
```

Sample output:
```
Available configurations:
- configs/config.yaml: Basic configuration for prompt testing
- configs/advanced_config.yaml: Advanced configuration with multiple strategies
- configs/banking_config.yaml: Configuration for testing banking assistant prompts
```

### Display Configuration Details

```bash
python -m cli.main config --show configs/config.yaml
```

Sample output:
```
Configuration: configs/config.yaml
---------------------------------
prompt: "You are a helpful assistant for a banking organization."
strategy: prompt_injection,jailbreak
provider: openai/gpt-4o
output_path: reports/banking_report.json
timeout: 30
temperature: 0.7
```

### Validate a Configuration

```bash
python -m cli.main config --validate configs/my_config.yaml
```

Sample output:
```
Validating configs/my_config.yaml...
✓ Configuration is valid!
```

Or if there are errors:
```
Validating configs/my_config.yaml...
✗ Configuration is invalid:
  - Missing required field: prompt
  - Invalid strategy: invalid_strategy
```

## See Also

- [Test Command](test.md) - For running prompt tests
- [Configuration Guide](../configuration/index.md) - For detailed configuration information
