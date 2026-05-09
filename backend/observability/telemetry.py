from prometheus_client import Counter, Histogram, Gauge
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
import time

REQUEST_COUNT = Counter(
    'ai_requests_total',
    'Total AI requests processed'
)

AI_LATENCY = Histogram(
    'ai_response_latency_seconds',
    'AI response latency'
)

TOKEN_USAGE = Counter(
    'llm_token_usage_total',
    'LLM token consumption'
)

ACTIVE_AGENTS = Gauge(
    'active_agents_total',
    'Currently running autonomous agents'
)

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint='http://otel-collector:4317'))
trace.get_tracer_provider().add_span_processor(span_processor)

class ObservabilityManager:
    async def track_ai_request(self, provider: str, tokens: int, latency: float):
        REQUEST_COUNT.inc()
        TOKEN_USAGE.inc(tokens)
        AI_LATENCY.observe(latency)

        return {
            'provider': provider,
            'tokens': tokens,
            'latency': latency
        }

    async def trace_agent_execution(self, agent_name: str):
        with tracer.start_as_current_span(agent_name):
            ACTIVE_AGENTS.inc()
            time.sleep(0.1)
            ACTIVE_AGENTS.dec()
