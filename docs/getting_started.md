# Getting Started with Compliant LLM

Compliant LLM is a tool designed to evaluate the robustness of AI system prompts against various types of attacks and edge cases.

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

## Quick Start

### Using the UI

Start the compliant-llm UI dashboard using the command:

```bash
compliant-llm dashboard
```

### Using the CLI

1. Create a configuration file or use the default one:

```yaml
prompt: |
  Your system prompt here...

provider_name: openai/gpt-4o
strategy: prompt_injection,adversarial
```

2. Connect to the LLM:

```bash
# for openai models:
export OPENAI_API_KEY=your_api_key_here

# for anthropic models:
export ANTHROPIC_API_KEY=your_api_key_here

# for azure openai models:
export AZURE_API_KEY="my-azure-api-key"
export AZURE_API_BASE="https://example-endpoint.openai.azure.com"
export AZURE_API_VERSION="2023-05-15"
```

3. Run the tool:

```bash
compliant-llm test --config configs/your_config.yaml
```

4. Or simply run the test with the following CLI arguments:

```bash
compliant-llm test --prompt "Your system prompt here..." --strategy "prompt_injection,adversarial" --provider "openai/gpt-4o"
```

5. View the results:

```bash
compliant-llm dashboard
```

## Next Steps

- Learn about [configuration options](./configuration.md)
