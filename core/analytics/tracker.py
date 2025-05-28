import os
import uuid
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# OpenTelemetry Tracing
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

# OpenTelemetry Metrics
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.metrics import set_meter_provider, get_meter_provider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
    ConsoleMetricExporter
)
from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter

# ----------------------------
# Client ID Handling
# ----------------------------
from .client import get_client_id

CLIENT_ID = get_client_id()

# ----------------------------
# Enums and Event Models
# ----------------------------
class EventType(str, Enum):
    USAGE = "usage"
    ERROR = "error"

class InteractionType(str, Enum):
    CLI = "cli"
    DASHBOARD = "dashboard"
    API = "api"
    BATCH = "batch"

class BaseEvent(BaseModel):
    name: str
    interaction_type: InteractionType
    client_id: str = Field(default_factory=get_client_id)
    type: EventType

class UsageEvent(BaseEvent):
    type: EventType = EventType.USAGE

class ErrorEvent(BaseEvent):
    error_msg: str
    type: EventType = EventType.ERROR

# ----------------------------
# OpenTelemetry Initialization
# ----------------------------

# Define common resource attributes
resource = Resource.create({
    SERVICE_NAME: "compliant-llm",
    "service.version": "1.0.0",
    "environment": os.getenv("ENVIRONMENT", "prod")
})

# ----- Initialize Metrics -----
try:
    instrumentation_key = os.getenv("AZURE_INSTRUMENTATION_KEY", "ed532436-db1f-46bb-aeef-17cb4f3dcf8b")
    ingestion_endpoint = os.getenv("AZURE_INGESTION_ENDPOINT", "https://westus-0.in.applicationinsights.azure.com/")

    metric_exporter = AzureMonitorMetricExporter(
        connection_string=f"InstrumentationKey={instrumentation_key};IngestionEndpoint={ingestion_endpoint}"
    )

    metric_readers = [
        PeriodicExportingMetricReader(ConsoleMetricExporter()),  # Optional for local debugging
        PeriodicExportingMetricReader(metric_exporter)
    ]

    meter_provider = MeterProvider(resource=resource, metric_readers=metric_readers)
    set_meter_provider(meter_provider)

    print("✅ Azure Monitor metrics initialized.")
except Exception as e:
    print(f"❌ Failed to initialize Azure Monitor metrics: {e}")

# ----- Initialize Tracing -----
try:
    trace_exporter = AzureMonitorTraceExporter(
        connection_string=f"InstrumentationKey={instrumentation_key};IngestionEndpoint={ingestion_endpoint}"
    )

    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer_provider = trace.get_tracer_provider()

    tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
    tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))  # Optional for local debugging

    print("✅ Azure Monitor traces initialized.")
except Exception as e:
    print(f"❌ Failed to initialize Azure Monitor tracing: {e}")

# ----------------------------
# Tracker Class (Traces + Metrics)
# ----------------------------
class AnalyticsTracker:
    def __init__(self):
        # Initialize tracer
        self.tracer = trace.get_tracer("compliant-llm")
        self.tracer_provider = trace.get_tracer_provider()
        
        if not self.tracer_provider:
            logger.warning("⚠️ No tracer provider available")
            self.tracer = None
            
        # Initialize metrics
        try:
            self.meter = get_meter_provider().get_meter("compliant-llm")
            self.usage_counter = self.meter.create_counter(
                name="compliant_llm.command_invocations",
                description="Number of times a CLI/dashboard/api command was invoked"
            )
            self.error_counter = self.meter.create_counter(
                name="compliant_llm.errors",
                description="Number of errors encountered"
            )
        except Exception as e:
            logger.error(f"⚠️ Metrics counters unavailable: {e}")
            self.usage_counter = None
            self.error_counter = None

    def track(self, event: BaseEvent):
        logger.info(f"TRACKING EVENT: {event.name} ({event.type.value})")
        
        if not self.tracer:
            logger.warning("⚠️ No tracer available")
            return
            
        # ----- Trace Span -----
        span_name = f"{event.type.value}:{event.name}"
        try:
            with self.tracer.start_as_current_span(span_name) as span:
                if span:  # Check if span was created successfully
                    span.set_attribute("client_id", event.client_id)
                    span.set_attribute("interaction_type", event.interaction_type.value)
                    span.set_attribute("event_type", event.type.value)
                    span.set_attribute("command", event.name)
                    if isinstance(event, ErrorEvent):
                        span.set_attribute("error_msg", event.error_msg[:100])
        except Exception as e:
            logger.error(f"❌ Error creating span: {e}")

        # ----- Metrics -----
        attributes = {
            "client_id": event.client_id,
            "interaction_type": event.interaction_type.value,
            "name": event.name
        }

        try:
            if event.type == EventType.USAGE and self.usage_counter:
                self.usage_counter.add(1, attributes)
            elif event.type == EventType.ERROR and self.error_counter:
                attributes["error_msg"] = getattr(event, "error_msg", "unknown")[:100]
                self.error_counter.add(1, attributes)
        except Exception as e:
            logger.error(f"❌ Error recording metrics: {e}")

# ----------------------------
# Decorator for Usage Tracking
# ----------------------------
def track_usage(name: str, interaction_type: InteractionType = InteractionType.CLI):
    def decorator(func):
        def wrapper(*args, **kwargs):
            event = UsageEvent(name=name, interaction_type=interaction_type)
            analytics_tracker.track(event)
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ----------------------------
# Tracker Instance
# ----------------------------
analytics_tracker = AnalyticsTracker()
