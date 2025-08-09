from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
import logging

try:  # Optional OpenTelemetry imports
    from opentelemetry import trace  # type: ignore
    from opentelemetry.sdk.trace import TracerProvider  # type: ignore
    OTEL_AVAILABLE = True
except ImportError:  # pragma: no cover - best effort fallback
    trace = None  # type: ignore
    TracerProvider = None  # type: ignore
    OTEL_AVAILABLE = False

from .config import settings

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
AGENT_QUERIES = Counter('agent_queries_total', 'Total agent queries', ['tenant_id', 'agent_type'])
ACTIVE_AGENTS = Gauge('active_agents', 'Number of active agent instances')
TRIAL_CONVERSIONS = Counter('trial_conversions_total', 'Trial to paid conversions')

def setup_monitoring():
    """Set up monitoring and tracing (graceful if optional deps missing)."""
    if settings.ENVIRONMENT == "production" and OTEL_AVAILABLE:
        trace.set_tracer_provider(TracerProvider())  # type: ignore
        logging.info("OpenTelemetry tracing initialized")
    elif settings.ENVIRONMENT == "production" and not OTEL_AVAILABLE:
        logging.warning("OpenTelemetry not installed; skipping tracing. Install opentelemetry-sdk to enable.")
    else:
        logging.info("Monitoring setup skipped in development")
