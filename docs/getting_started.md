# Getting Started with FC Prompt Tester

FC Prompt Tester is a tool designed to evaluate the robustness of AI system prompts against various types of attacks and edge cases.

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
```

3. Run the tool:

```bash
fc-test --config configs/your_config.yaml
```

4. View the results:

```bash
fc-ui
```

## Next Steps

- Explore different [testing strategies](./testing_strategies.md)
- Learn about [configuration options](./configuration.md)
- Check out the [examples](../examples/)
