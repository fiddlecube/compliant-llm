import os
import time
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.metrics import set_meter_provider, get_meter_provider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter

# Define the resource attributes for metrics
resource = Resource.create({
    SERVICE_NAME: "compliant-llm",
    "service.version": "1.0.0",
    "environment": os.getenv("ENVIRONMENT", "prod")
})

# Configure Azure Monitor connection
try:
    # Get Azure Monitor configuration from environment variables
    instrumentation_key = os.getenv("AZURE_INSTRUMENTATION_KEY", "ed532436-db1f-46bb-aeef-17cb4f3dcf8b")
    ingestion_endpoint = os.getenv("AZURE_INGESTION_ENDPOINT", "https://westus-0.in.applicationinsights.azure.com/")

    # Create Azure Monitor exporter
    exporter = AzureMonitorMetricExporter(
        connection_string=(
            f"InstrumentationKey={instrumentation_key};"
            f"IngestionEndpoint={ingestion_endpoint}"
        )
    )
    print("✅ Azure Monitor exporter successfully initialized.")
except Exception as e:
    print(f"❌ Failed to initialize Azure Monitor exporter: {e}")
    print("❌ Falling back to console exporter only.")
    exporter = None

# Create a test metric to verify connection if Azure is enabled
if exporter:

    # Set up the metric provider with exporters
    metric_readers = [
        # Local debugging
        PeriodicExportingMetricReader(ConsoleMetricExporter()),
        # Azure Monitor Exporter (always try to use Azure unless explicitly disabled)
        PeriodicExportingMetricReader(exporter)
    ]
    
    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=metric_readers
    )

set_meter_provider(meter_provider)
meter = get_meter_provider().get_meter("compliant-llm")

class AnalyticsTracker:
    """Class for tracking analytics and metrics with Azure Monitor via OpenTelemetry."""

    def __init__(self):
        self.total_tests = meter.create_counter("compliant_llm.total_tests", description="Total number of tests executed", unit="1")
        self.success_count = meter.create_counter("compliant_llm.success_count", description="Number of successful attacks", unit="1")
        self.test_duration = meter.create_histogram("compliant_llm.test_duration", description="Duration of each test in seconds", unit="s")
        self.strategy_usage = meter.create_counter("compliant_llm.strategy_usage", description="Usage count per attack strategy", unit="1")
        self.provider_usage = meter.create_counter("compliant_llm.provider_usage", description="Usage count per LLM provider", unit="1")
        self.prompt_length_hist = meter.create_histogram("compliant_llm.prompt_length", description="Length of prompts in characters", unit="chars")
        self.api_response_time = meter.create_histogram("compliant_llm.api_response_time", description="API response time in seconds", unit="s")
        self.errors = meter.create_counter("compliant_llm.errors", description="Number of errors encountered", unit="1")
        self.cli_command_usage = meter.create_counter("compliant_llm.cli_command_usage", description="Count of CLI commands executed", unit="1")
        self.template_usage = meter.create_counter("compliant_llm.template_usage", description="Usage count per config/prompt template", unit="1")
        self.report_view_usage = meter.create_counter("compliant_llm.report_view_usage", description="Report view interactions", unit="1")
        self.config_validation = meter.create_counter("compliant_llm.config_validation", description="Configuration validation result", unit="1")

    def track_test_start(self, strategy_name: str, provider_name: str) -> float:
        self.total_tests.add(1)
        self.strategy_usage.add(1, {"strategy": strategy_name})
        self.provider_usage.add(1, {"provider": provider_name})
        return time.time()

    def track_test_end(self, start_time: float, success: bool):
        duration = time.time() - start_time
        self.test_duration.record(duration)
        if success:
            self.success_count.add(1)

    def track_api_response(self, response_time: float, provider: str):
        self.api_response_time.record(response_time, {"provider": provider})

    def track_error(self, error_type: str, error_message: str):
        self.errors.add(1, {"type": error_type, "message": error_message[:100]})

    def track_cli_command(self, command_name: str):
        self.cli_command_usage.add(1, {"command": command_name})

    def track_template_use(self, template_type: str, template_name: str):
        self.template_usage.add(1, {
            "type": template_type,
            "template": template_name
        })

    def track_report_view(self, format: str, summary: bool):
        self.report_view_usage.add(1, {
            "format": format,
            "summary": str(summary)
        })

    def track_config_validation(self, result: str):
        self.config_validation.add(1, {"result": result})

# Initialize global tracker
analytics_tracker = AnalyticsTracker()