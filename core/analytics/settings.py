import os

def get_azure_settings():
    """Get Azure Monitor settings from environment variables."""
    return {
        "instrumentation_key": os.getenv("AZURE_INSTRUMENTATION_KEY", "ed532436-db1f-46bb-aeef-17cb4f3dcf8b"),
        "ingestion_endpoint": os.getenv("AZURE_INGESTION_ENDPOINT", "https://westus-0.in.applicationinsights.azure.com/"),
    }

azure_settings = get_azure_settings()
