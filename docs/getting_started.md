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

1. Create a configuration file or use the default one:

```yaml
prompt: |
  Your system prompt here...

provider_name: openai/gpt-4o
strategy: prompt_injection,adversarial
```

2. Set up your API keys in a `.env` file:

```
OPENAI_API_KEY=your_api_key_here
ANTHROPIC_API_KEY=your_api_key_here
```

3. Run the tool:

```bash
compliant-llm test --config configs/your_config.yaml
```

4. View the results:

```bash
compliant-llm ui
```

## Next Steps

- Learn about [configuration options](./configuration.md)
