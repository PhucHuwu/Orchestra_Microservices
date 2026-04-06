from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

MESSAGES_PROCESSED_TOTAL = Counter(
    "mixer_messages_processed_total",
    "Total number of processed instrument output messages",
    labelnames=("instrument",),
)

MAPPING_ERRORS_TOTAL = Counter(
    "mixer_mapping_errors_total",
    "Total number of mapping errors",
    labelnames=("instrument",),
)

PUBLISH_ERRORS_TOTAL = Counter(
    "mixer_publish_errors_total",
    "Total number of publish errors",
    labelnames=("instrument",),
)

LATENCY_MS = Histogram(
    "mixer_event_latency_ms",
    "Latency from instrument render to mixer emit in milliseconds",
    labelnames=("instrument",),
    buckets=(1, 5, 10, 20, 50, 100, 200, 500, 1000, 5000),
)


def metrics_payload() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST
