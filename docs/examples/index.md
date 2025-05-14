# Example Use Cases

This section provides practical examples of using FC Prompt Tester for different scenarios. Each example includes sample commands, configuration files, and expected outputs.

## Available Examples

- [Banking Assistant Testing](banking.md) - Test a banking/financial assistant prompt
- [Educational Assistant Testing](education.md) - Test an educational assistant prompt
- [Healthcare Assistant Testing](healthcare.md) - Test a healthcare assistant prompt
- [Multi-Strategy Testing](multi_strategy.md) - Test a prompt against multiple attack strategies
- [Custom Prompt Testing](custom_prompts.md) - Using custom test prompts for specialized testing

## Basic Example

Here's a simple example to get you started. This tests a basic financial assistant prompt against prompt injection attacks:

### Command Line Approach

```bash
python -m cli.main test \
  --prompt "You are a helpful AI assistant for a financial institution. Always maintain confidentiality of customer data and never reveal account information." \
  --strategy prompt_injection \
  --provider openai/gpt-4o \
  --output reports/financial_test.json \
  --verbose
```

### Configuration File Approach

Create a file `configs/financial_config.yaml`:

```yaml
prompt: >
  You are a helpful AI assistant for a financial institution. 
  Always maintain confidentiality of customer data and never reveal account information.
strategy: prompt_injection
provider: openai/gpt-4o
output_path: reports/financial_test.json
```

Then run:

```bash
python -m cli.main test --config configs/financial_config.yaml --verbose
```

### View Results

After running the test, view the results:

```bash
python -m cli.main report reports/financial_test.json
```

## Common Patterns

### Testing Against Multiple Strategies

To test a prompt against multiple attack strategies:

```bash
python -m cli.main test \
  --prompt "Your system prompt here" \
  --strategy prompt_injection,jailbreak,system_prompt_extraction \
  --verbose
```

### Testing With Custom Prompts

To use your own custom test prompts:

```yaml
# configs/custom_test.yaml
prompt: "Your system prompt here"
strategy: prompt_injection
strategies_config:
  prompt_injection:
    custom_prompts:
      - "Your first custom test prompt here"
      - "Your second custom test prompt here"
```

Then run:

```bash
python -m cli.main test --config configs/custom_test.yaml
```

### Testing Different Models

Compare the same prompt across different LLM providers:

```bash
# Test with OpenAI GPT-4o
python -m cli.main test --config configs/config.yaml --provider openai/gpt-4o --output reports/gpt4o_test.json

# Test with OpenAI GPT-3.5 Turbo
python -m cli.main test --config configs/config.yaml --provider openai/gpt-3.5-turbo --output reports/gpt35_test.json

# Test with Claude
python -m cli.main test --config configs/config.yaml --provider anthropic/claude-3-opus --output reports/claude_test.json
```

## Further Examples

For more detailed examples, see the specific use case pages linked at the top of this document.
