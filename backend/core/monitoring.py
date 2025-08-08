from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
from opentelemetry import trace
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import logging

from .config import settings

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
AGENT_QUERIES = Counter('agent_queries_total', 'Total agent queries', ['tenant_id', 'agent_type'])
ACTIVE_AGENTS = Gauge('active_agents', 'Number of active agent instances')
TRIAL_CONVERSIONS = Counter('trial_conversions_total', 'Trial to paid conversions')

def setup_monitoring():
    """Set up monitoring and tracing."""
    if settings.ENVIRONMENT == "production":
        # Set up OpenTelemetry tracing
        trace.set_tracer_provider(TracerProvider())
        tracer = trace.get_tracer(__name__)
        
        # Set up Prometheus metrics
        logging.info("Monitoring initialized")
    else:
        logging.info("Monitoring setup skipped in development")
