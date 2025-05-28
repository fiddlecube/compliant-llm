import os
import uuid
import time
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.metrics import set_meter_provider, get_meter_provider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter

# ----------------------------
# Client ID Handling
# ----------------------------
from .client import get_client_id

CLIENT_ID = get_client_id()

# ----------------------------
# Enums and Base Schema
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
# OTEL + Azure Exporter Setup
# ----------------------------
resource = Resource.create({
    SERVICE_NAME: "compliant-llm",
    "service.version": "1.0.0",
    "environment": os.getenv("ENVIRONMENT", "prod")
})

try:
    instrumentation_key = os.getenv("AZURE_INSTRUMENTATION_KEY", "ed532436-db1f-46bb-aeef-17cb4f3dcf8b")
    ingestion_endpoint = os.getenv("AZURE_INGESTION_ENDPOINT", "https://westus-0.in.applicationinsights.azure.com/")
    exporter = AzureMonitorMetricExporter(
        connection_string=f"InstrumentationKey={instrumentation_key};IngestionEndpoint={ingestion_endpoint}"
    )
    print("✅ Azure Monitor exporter initialized.")
except Exception as e:
    print(f"❌ Azure Monitor exporter failed: {e}")
    exporter = None

if exporter:
    readers = [
        PeriodicExportingMetricReader(ConsoleMetricExporter()),
        PeriodicExportingMetricReader(exporter)
    ]
    meter_provider = MeterProvider(resource=resource, metric_readers=readers)
    set_meter_provider(meter_provider)

meter = get_meter_provider().get_meter("compliant-llm")

# ----------------------------
# Tracker Class
# ----------------------------
class AnalyticsTracker:
    def __init__(self):
        self.usage_counter = meter.create_counter("compliant_llm.command_invocations", description="Command invocations")
        self.error_counter = meter.create_counter("compliant_llm.errors", description="Error events")

    def track(self, event: BaseEvent):
        if event.type == EventType.USAGE:
            self.usage_counter.add(1, {
                "name": event.name,
                "interaction_type": event.interaction_type,
                "client_id": event.client_id
            })
        elif event.type == EventType.ERROR:
            self.error_counter.add(1, {
                "name": event.name,
                "interaction_type": event.interaction_type,
                "client_id": event.client_id,
                "message": getattr(event, "error_msg", "unknown")[:100]
            })


analytics_tracker = AnalyticsTracker()

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

