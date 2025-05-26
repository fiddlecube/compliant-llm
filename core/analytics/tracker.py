import os
import time
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.metrics import set_meter_provider, get_meter_provider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from prometheus_client import start_http_server

# Start Prometheus scrape server (default on port 9090)
# start_http_server(port=9090)

# Initialize OpenTelemetry metrics
meter_provider = MeterProvider(
    metric_readers=[
        # Console for local debugging
        PeriodicExportingMetricReader(ConsoleMetricExporter()),

        # # OTLP Exporter for production
        PeriodicExportingMetricReader(
            OTLPMetricExporter(
                endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
            )
        ),
        # PrometheusMetricReader()
    ]
)

set_meter_provider(meter_provider)
meter = get_meter_provider().get_meter("compliant-llm")

class AnalyticsTracker:
    """Class for tracking analytics and metrics."""

    def __init__(self):
        self.total_tests = meter.create_counter(
            "compliant_llm.total_tests",
            description="Total number of tests executed",
            unit="1",
        )
        self.success_count = meter.create_counter(
            "compliant_llm.success_count",
            description="Number of successful attacks",
            unit="1",
        )
        self.test_duration = meter.create_histogram(
            "compliant_llm.test_duration",
            description="Duration of each test in seconds",
            unit="s",
        )
        self.strategy_usage = meter.create_counter(
            "compliant_llm.strategy_usage",
            description="Usage count per attack strategy",
            unit="1",
        )
        self.provider_usage = meter.create_counter(
            "compliant_llm.provider_usage",
            description="Usage count per LLM provider",
            unit="1",
        )
        self.prompt_length_hist = meter.create_histogram(
            "compliant_llm.prompt_length",
            description="Length of prompts in characters",
            unit="chars",
        )
        self.api_response_time = meter.create_histogram(
            "compliant_llm.api_response_time",
            description="API response time in seconds",
            unit="s",
        )
        self.errors = meter.create_counter(
            "compliant_llm.errors",
            description="Number of errors encountered",
            unit="1",
        )
        self.nist_compliance = meter.create_counter(
            "compliant_llm.nist_compliance",
            description="NIST compliance status",
            unit="1",
        )

    def track_test_start(self, strategy_name: str, provider_name: str):
        self.total_tests.add(1)
        self.strategy_usage.add(1, {"strategy": strategy_name})
        self.provider_usage.add(1, {"provider": provider_name})
        self.start_time = time.time()

    def track_test_end(self, success: bool):
        duration = time.time() - self.start_time
        self.test_duration.record(duration)
        if success:
            self.success_count.add(1)

    def track_prompt_length(self, prompt: str, prompt_type: str):
        self.prompt_length_hist.record(len(prompt), {"type": prompt_type})

    def track_api_response(self, response_time: float, tokens: int, provider: str):
        self.api_response_time.record(response_time, {"provider": provider})

    def track_error(self, error_type: str, error_message: str):
        self.errors.add(1, {"type": error_type, "message": error_message[:100]})

    def track_nist_compliance(self, is_compliant: bool, category: str):
        self.nist_compliance.add(1, {
            "category": category,
            "status": "pass" if is_compliant else "fail"
        })

# Initialize global tracker
analytics_tracker = AnalyticsTracker()
