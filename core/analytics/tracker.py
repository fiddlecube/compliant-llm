import os
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

# OpenTelemetry core
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter, AzureMonitorMetricExporter

# OpenTelemetry metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.metrics import set_meter_provider, get_meter_provider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
)

# ----------------------------
# Opt-out utility
# ----------------------------
def is_analytics_enabled() -> bool:
    return os.getenv("DISABLE_COMPLIANT_LLM_TELEMETRY", "false").lower() != "true"

# ----------------------------
# Client ID utility (you should define this)
# ----------------------------
from .client import get_client_id

# ----------------------------
# Event Type Enums and Models
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
    client_id: Optional[str] = Field(default_factory=get_client_id)
    type: EventType

class UsageEvent(BaseEvent):
    type: EventType = EventType.USAGE

class ErrorEvent(BaseEvent):
    error_msg: str
    type: EventType = EventType.ERROR

# ----------------------------
# Tracker Class
# ----------------------------
class AnalyticsTracker:
    def __init__(self):
        self.enabled = is_analytics_enabled()
        if not self.enabled:
            self.tracer = None
            self.usage_counter = None
            self.error_counter = None
            return

        from .settings import azure_settings
        
        instrumentation_key = azure_settings["instrumentation_key"]
        ingestion_endpoint = azure_settings["ingestion_endpoint"]

        # Resource
        resource = Resource.create({
            SERVICE_NAME: "compliant-llm",
            "service.version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "prod")
        })

        # Initialize tracing
        try:
            trace_exporter = AzureMonitorTraceExporter(
                connection_string=f"InstrumentationKey={instrumentation_key};IngestionEndpoint={ingestion_endpoint}"
            )
            trace.set_tracer_provider(TracerProvider(resource=resource))
            tracer_provider = trace.get_tracer_provider()
            tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
            self.tracer = trace.get_tracer("compliant-llm")
        except Exception as e:
            self.tracer = None

        # Initialize metrics
        try:
            metric_exporter = AzureMonitorMetricExporter(
                connection_string=f"InstrumentationKey={instrumentation_key};IngestionEndpoint={ingestion_endpoint}"
            )
            metric_readers = [
                PeriodicExportingMetricReader(metric_exporter)
            ]
            meter_provider = MeterProvider(resource=resource, metric_readers=metric_readers)
            set_meter_provider(meter_provider)
            self.meter = get_meter_provider().get_meter("compliant-llm")
            self.usage_counter = self.meter.create_counter(
                name="compliant_llm.command_invocations",
                description="Number of CLI/dashboard/API commands invoked"
            )
            self.error_counter = self.meter.create_counter(
                name="compliant_llm.errors",
                description="Number of errors encountered"
            )
        except Exception as e:
            self.usage_counter = None
            self.error_counter = None

    def track(self, event: BaseEvent):
        if not self.enabled:
            return  # Opted out

        # --- Tracing ---
       
        with self.tracer.start_as_current_span(f"{event.type.value}:{event.name}") as span:
            span.set_attribute("interaction_type", event.interaction_type.value)
            span.set_attribute("event_type", event.type.value)
            span.set_attribute("command", event.name)
            if event.client_id:
                span.set_attribute("client_id", event.client_id)
            if isinstance(event, ErrorEvent):
                span.set_attribute("error_msg", event.error_msg[:100])

        # --- Metrics ---
        attributes = {
            "interaction_type": event.interaction_type.value,
            "name": event.name
        }
        if event.client_id:
            attributes["client_id"] = event.client_id
        if isinstance(event, ErrorEvent):
            attributes["error_msg"] = event.error_msg[:100]

       
        if event.type == EventType.USAGE and self.usage_counter:
            self.usage_counter.add(1, attributes)
        elif event.type == EventType.ERROR and self.error_counter:
            self.error_counter.add(1, attributes)

# ----------------------------
# Usage Tracking Decorator
# ----------------------------
def track_usage(name: str, interaction_type: InteractionType = None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if analytics_tracker.enabled:
                event = UsageEvent(name=name, interaction_type=interaction_type)
                analytics_tracker.track(event)
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ----------------------------
# Global Tracker Instance
# ----------------------------
analytics_tracker = AnalyticsTracker()
