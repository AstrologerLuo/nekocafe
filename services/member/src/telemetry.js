/**
 * OpenTelemetry 集成 - 会员服务
 * Traces → OTLP → Tempo
 * Metrics → Prometheus
 * Logs → 结构化 JSON（由 Loki 采集）
 */
'use strict';

function setupTelemetry() {
  const endpoint = process.env.OTEL_EXPORTER_OTLP_ENDPOINT;
  const serviceName = process.env.OTEL_SERVICE_NAME || 'member-svc';

  if (!endpoint) {
    process.stderr.write(JSON.stringify({
      timestamp: new Date().toISOString(),
      level: 'WARN',
      service: serviceName,
      message: 'OTEL_EXPORTER_OTLP_ENDPOINT not set, telemetry disabled',
    }) + '\n');
    return;
  }

  try {
    const { NodeSDK } = require('@opentelemetry/sdk-node');
    const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');
    const { Resource } = require('@opentelemetry/resources');
    const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');
    const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');

    const sdk = new NodeSDK({
      resource: new Resource({
        [SemanticResourceAttributes.SERVICE_NAME]: serviceName,
        [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
        'deployment.environment': process.env.APP_ENV || 'dev',
      }),
      traceExporter: new OTLPTraceExporter({ url: endpoint }),
      instrumentations: [getNodeAutoInstrumentations()],
    });

    sdk.start();

    process.on('SIGTERM', () => sdk.shutdown());

    process.stdout.write(JSON.stringify({
      timestamp: new Date().toISOString(),
      level: 'INFO',
      service: serviceName,
      message: 'OpenTelemetry initialized',
      endpoint,
    }) + '\n');
  } catch (e) {
    process.stderr.write(JSON.stringify({
      timestamp: new Date().toISOString(),
      level: 'WARN',
      service: serviceName,
      message: `OpenTelemetry setup failed: ${e.message}. Continuing without telemetry.`,
    }) + '\n');
  }
}

module.exports = { setupTelemetry };
