# LLM Providers

Compliant LLM supports various LLM providers through the LiteLLM library. This section provides information on setting up and using different providers with Compliant LLM.

## Supported Providers

- [OpenAI](openai.md)
- [Anthropic](anthropic.md)
- [Azure](azure.md)
- [Google](google.md)
- [vLLM](vllm.md)

## General Setup

1. Install the required dependencies:
   ```bash
   pip install compliant-llm[all]
   ```

2. Set up the necessary API keys as environment variables or in a `.env` file.

3. Use the `--provider` flag when running tests to specify the desired provider:
   ```bash
   compliant-llm test --prompt "Your prompt here" --provider "openai/gpt-3.5-turbo"
   ```

For provider-specific setup instructions and usage examples, refer to the individual provider pages linked above, or refer to [LiteLLM provider docs](https://docs.litellm.ai/docs/providers) for more information.
