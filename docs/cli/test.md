# Test Command

The `test` command is the primary function of Compliant LLM, allowing you to evaluate system prompts against various attack strategies.

## Synopsis

```bash
python -m cli.main test [OPTIONS]
```

## Description

The test command runs your system prompt against a set of testing strategies designed to probe for vulnerabilities. Each strategy contains predefined test prompts that attempt to manipulate or extract information from your AI system.

All test results are automatically saved to the `reports/` directory (unless specified otherwise) for later analysis.

## Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--config` | `-c` | Path to configuration file | None |
| `--prompt` | `-p` | Direct input of system prompt | None |
| `--strategy` | `-s` | Comma-separated list of test strategies | `prompt_injection` |
| `--provider` | `-m` | LLM provider to use | `openai/gpt-4o` |
| `--output` | `-o` | Output file path | `reports/report.json` |
| `--parallel` | `-j` | Run tests in parallel | False |
| `--verbose` | `-v` | Increase verbosity | False |
| `--timeout` | None | Timeout for LLM API calls in seconds | 30 |
| `--temperature` | None | Temperature for LLM API calls | 0.7 |

## Available Testing Strategies

| Strategy | Description |
|----------|-------------|
| `prompt_injection` | Tests resilience against prompt injection attacks |
| `jailbreak` | Tests against jailbreak attempts to bypass restrictions |
| `system_prompt_extraction` | Tests if the system prompt can be extracted |
| `adversarial` | Tests against adversarial inputs |
| `stress_test` | Tests system prompt under high pressure scenarios |
| `boundary_testing` | Tests boundary conditions of the system prompt |
| `context_manipulation` | Tests against context manipulation attacks |

## Input Methods

You can provide the system prompt in two ways:

1. **Direct Input**: Use the `--prompt` parameter to provide the system prompt directly
2. **Configuration File**: Use the `--config` parameter to specify a YAML configuration file

## Examples

### Basic Usage

Test a prompt using the default strategy (prompt injection):

```bash
python -m cli.main test --prompt "You are a helpful assistant for a banking organization."
```

### Multiple Strategies

Test against multiple attack strategies:

```bash
python -m cli.main test --prompt "You are a helpful assistant." \
  --strategy prompt_injection,jailbreak,adversarial
```

### Using a Configuration File

Test using settings from a YAML configuration file:

```bash
python -m cli.main test --config configs/config.yaml
```

### Custom Output Path

Specify a custom output path for the report:

```bash
python -m cli.main test --prompt "You are a helpful assistant." \
  --output reports/custom_report.json
```

### Parallel Execution

Run tests in parallel for faster execution:

```bash
python -m cli.main test --config configs/config.yaml --parallel
```

### Verbose Output

Enable verbose output for more detailed information:

```bash
python -m cli.main test --prompt "You are a helpful assistant." --verbose
```

## See Also

- [Report Command](report.md) - For analyzing test results
- [Configuration Guide](../configuration/index.md) - For creating configuration files
