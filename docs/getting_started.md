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

#### Create a configuration file or use the default one:

```yaml
prompt: |
  Your system prompt here...

provider_name: openai/gpt-4o
strategy: prompt_injection,adversarial
```

#### Connect to the LLM:

##### For OpenAI models

```bash
export OPENAI_API_KEY=your_api_key_here
```

##### For Anthropic models

```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

##### For Azure OpenAI models

```bash
export AZURE_API_KEY="my-azure-api-key"
export AZURE_API_BASE="https://example-endpoint.openai.azure.com"
export AZURE_API_VERSION="2023-05-15"
```

#### Run the tool

```bash
compliant-llm test --config configs/your_config.yaml
```

#### Or simply run the test with the following CLI arguments:

```bash
compliant-llm test --prompt "Your system prompt here..." --strategy "prompt_injection,adversarial" --provider "openai/gpt-4o"
```

#### View the results:

```bash
compliant-llm dashboard
```

## Next Steps

- Learn about [configuration options](./configuration.md)
