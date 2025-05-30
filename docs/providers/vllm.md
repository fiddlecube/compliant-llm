# To set up vllm do the following:

1. Install vllm
2. Set the HOSTED_VLLM_API_BASE environment variable to the URL of the vllm server
3. Set the HOSTED_VLLM_API_KEY environment variable to the API key of the vllm server (if any)


Run from the CLI:
```
compliant-llm test --prompt "test" --provider "hosted_vllm/<your_model_name>"
--strategy  "jailbreak"
```

Run from the UI:
```bash
compliant-llm dashboard
```

1. Select Provider as `vLLM ollama`
2. Enter Model as `<your_model>`
3. Enter Hosted LLM API Base as `<your_api_base>`