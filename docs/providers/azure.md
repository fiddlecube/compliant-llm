# To set up Azure do the following:

```bash
export AZURE_API_KEY="my-azure-api-key"
export AZURE_API_BASE="https://example-endpoint.openai.azure.com"
export AZURE_API_VERSION="2023-05-15"

# optional
export AZURE_AD_TOKEN=""
export AZURE_API_TYPE=""
```


Run from the CLI:
```bash
compliant-llm test --prompt "test" --provider "azure/<your_deployment_name>"
--strategy  "jailbreak"
```

Run from the UI:
```bash
compliant-llm dashboard
```

1. Provider: `Azure`
2. Model: `<your_deployment_name>`
3. Azure API Key: `<your_api_key>`
4. Azure API Base: `<your_api_base>`
5. Azure API Version: `<your_api_version>`