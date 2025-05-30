# To set up vllm do the following:

1. Install vllm
2. Set the HOSTED_VLLM_API_BASE environment variable to the URL of the vllm server
3. Set the HOSTED_VLLM_API_KEY environment variable to the API key of the vllm server (if any)

### Start the UI Dashboard:
```bash
compliant-llm dashboard
```

In the UI, select:
1. Provider: `vLLM ollama`
2. Model: `<your_model>`
3. Hosted LLM API Base: `<your_api_base>`

### Run red-teaming using the CLI:
```
compliant-llm test --prompt "test" --provider "hosted_vllm/<your_model_name>"
--strategy  "jailbreak"
```