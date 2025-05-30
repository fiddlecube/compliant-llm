# To set up Azure do the following:

```bash
import os
os.environ["AZURE_API_KEY"] = "" # "my-azure-api-key"
os.environ["AZURE_API_BASE"] = "" # "https://example-endpoint.openai.azure.com"
os.environ["AZURE_API_VERSION"] = "" # "2023-05-15"

# optional
os.environ["AZURE_AD_TOKEN"] = ""
os.environ["AZURE_API_TYPE"] = ""
```


Run from the CLI:
compliant-llm test --prompt "test" --provider "azure/<your_deployment_name>"
--strategy  "jailbreak"

Run from the UI:
```bash
compliant-llm dashboard
```

1. Select Provider as `Azure OpenAI`
2. Enter Model as `<your_model>`
3. Enter Azure API Key as `<your_api_key>`
4. Enter Azure API Base as `<your_api_base>`
5. Enter Azure API Version as `<your_api_version>`