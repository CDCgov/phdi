from opentelemetry import trace

# Integrate services tracer with automatic instrumentation context
tracer = trace.get_tracer("orchestration_handlers.py_tracer")
