PROVIDERS = [
    {"name": "OpenAI", "value": "openai"},
    {"name": "Anthropic", "value": "anthropic"},
    {"name": "Google", "value": "google"},
    {"name": "Azure/OpenAI", "value": "azure_openai"},
]

PROVIDER_SETUP = [
    {"name": "OpenAI", "value": "openai", "openai_api_key": "","default_model": "gpt-4o"},
    {"name": "Anthropic", "value": "anthropic", "anthropic_api_key": "","default_model": "claude-3-5-sonnet"},
    {"name": "Gemini", "value": "gemini", "gemini_api_key": "","default_model": "gemini-2.0-flash-exp"},
    {"name": "Azure/OpenAI", "value": "azure_openai", "azure_openai_api_key": "", "azure_api_base": "", "azure_api_version": "","default_model": "gpt-4o"},
]