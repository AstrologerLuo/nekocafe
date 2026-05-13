"""OpenTelemetry 集成配置 - 预约服务"""
import os
import logging

logger = logging.getLogger(__name__)


def setup_telemetry() -> None:
    """
    初始化 OpenTelemetry 三件套：
    - Traces → OTLP → Tempo
    - Metrics → Prometheus Exporter
    - Logs → 结构化 JSON（通过 Loki 采集）
    """
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    service_name = os.getenv("OTEL_SERVICE_NAME", "reservation-svc")

    if not endpoint:
        logger.warning("OTEL_EXPORTER_OTLP_ENDPOINT not set, telemetry disabled")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

        # 资源标签
        resource = Resource.create({
            "service.name": service_name,
            "service.version": "1.0.0",
            "deployment.environment": os.getenv("APP_ENV", "dev"),
        })

        # Tracer Provider
        tracer_provider = TracerProvider(resource=resource)
        otlp_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
        tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        trace.set_tracer_provider(tracer_provider)

        # 自动埋点
        FastAPIInstrumentor().instrument()
        SQLAlchemyInstrumentor().instrument()

        logger.info("OpenTelemetry initialized", extra={"endpoint": endpoint, "service": service_name})

    except ImportError as e:
        logger.warning(f"OpenTelemetry packages not installed: {e}. Continuing without telemetry.")
