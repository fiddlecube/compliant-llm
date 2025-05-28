def get_azure_settings():
    """Get Azure Monitor settings."""
    return {
        "instrumentation_key": "ed532436-db1f-46bb-aeef-17cb4f3dcf8b",
        "ingestion_endpoint": "https://westus-0.in.applicationinsights.azure.com/",
    }

azure_settings = get_azure_settings()
