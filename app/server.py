"""Small instrumented Flask app for the DevOps observability capstone."""
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, Response, g, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from opentelemetry import context, trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.trace import SpanKind, Status, StatusCode

SERVICE = os.environ.get("OTEL_SERVICE_NAME", "demo-api")
Path("/app/logs").mkdir(exist_ok=True, parents=True)
app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

# HTTP requests can be grouped by status, method and route in Prometheus.
REQUESTS = Counter("http_requests_total", "Number of HTTP requests", ["method", "route", "status"])
LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP latency in seconds", ["method", "route"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

provider = TracerProvider(resource=Resource.create({"service.name": SERVICE, "deployment.environment": "local-demo"}))
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(
    endpoint=os.environ.get("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT", "http://otel-collector:4318/v1/traces")
)))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("capstone2.demo-api")

logger = logging.getLogger("capstone2")
logger.setLevel(logging.INFO)
logger.propagate = False
formatter = logging.Formatter("%(message)s")
file_handler = logging.FileHandler("/app/logs/app.jsonl")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def log_event(level, message, **kwargs):
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "service": SERVICE, "level": level, "message": message, **kwargs,
    }
    getattr(logger, level.lower(), logger.info)(json.dumps(event, separators=(",", ":")))


@app.before_request
def start_request():
    if request.path in ("/metrics", "/healthz"):
        return
    g.started_at = time.perf_counter()
    g.span = tracer.start_span(f"{request.method} {request.path}", kind=SpanKind.SERVER)
    g.ctx_token = context.attach(trace.set_span_in_context(g.span))


@app.after_request
def observe_request(response):
    if not hasattr(g, "span"):
        return response
    duration = time.perf_counter() - g.started_at
    route = request.url_rule.rule if request.url_rule else "unmatched"
    REQUESTS.labels(request.method, route, str(response.status_code)).inc()
    LATENCY.labels(request.method, route).observe(duration)
    g.span.set_attribute("http.request.method", request.method)
    g.span.set_attribute("url.path", request.path)
    g.span.set_attribute("http.response.status_code", response.status_code)
    g.span.set_attribute("http.route", route)
    if response.status_code >= 500:
        g.span.set_status(Status(StatusCode.ERROR, f"HTTP {response.status_code}"))
    trace_id = format(g.span.get_span_context().trace_id, "032x")
    response.headers["X-Trace-ID"] = trace_id
    log_event("ERROR" if response.status_code >= 500 else "INFO", "request_finished",
              method=request.method, route=route, status=response.status_code,
              duration_ms=round(duration * 1000, 2), trace_id=trace_id)
    g.span.end()
    context.detach(g.ctx_token)
    return response


@app.route("/healthz")
def health():
    return {"ok": True, "service": SERVICE}


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.route("/api/ok")
def healthy_request():
    with tracer.start_as_current_span("validate_healthy_request"):
        return {"ok": True, "message": "Healthy request completed"}


@app.route("/api/slow")
def slow_request():
    try:
        millis = max(0, min(1500, int(request.args.get("ms", "350"))))
    except ValueError:
        millis = 350
    with tracer.start_as_current_span("simulated_database_call") as child:
        child.set_attribute("db.system", "demo-simulation")
        time.sleep(millis / 1000)
    return {"ok": True, "latency_simulated_ms": millis}


@app.route("/api/fail")
def failing_request():
    with tracer.start_as_current_span("simulated_dependency_failure") as child:
        child.set_status(Status(StatusCode.ERROR, "Simulated dependency outage"))
        child.set_attribute("error.type", "simulated_dependency_outage")
        log_event("ERROR", "simulated_dependency_unavailable", trace_id=format(child.get_span_context().trace_id, "032x"))
    return {"ok": False, "error": "Demo-only simulated upstream outage"}, 503


@app.route("/runbook")
def runbook():
    body = Path("/app/docs/RUNBOOK.md").read_text(encoding="utf-8")
    return Response(body, mimetype="text/plain")


@app.route("/")
def index():
    return """<!doctype html><html lang='en'><head><meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Ship It & Keep It Running • Capstone 2</title>
<style>body{font-family:system-ui,Arial;background:#0c1427;color:#edf2ff;margin:0;padding:48px 18px}
main{max-width:870px;margin:auto}h1{font-size:2.4rem;line-height:1.2}p{color:#afbdd6;line-height:1.6}
.card{background:#18243a;border:1px solid #36445d;padding:24px;border-radius:15px;margin:20px 0}
a{color:#8fd3ff;text-decoration:none}.btn{display:inline-block;margin:4px 5px 4px 0;padding:11px 15px;
background:#2167d5;color:white;border-radius:8px;font-weight:600}.btn.alt{background:#33415f}
code{background:#101a2c;padding:3px 6px;border-radius:5px}small{color:#aab9cf}</style></head><body><main>
<small>DEVOPS CAPSTONE • OBSERVABILITY DEMO</small><h1>Ship it. Monitor it. Recover it.</h1>
<p>This instrumented demo API sends <b>metrics to Prometheus</b>, <b>logs to Loki</b>, and <b>request traces to Tempo</b>, all visualized in Grafana.</p>
<div class='card'><h2>1. Generate sample requests</h2>
<a class='btn' href='/api/ok' target='_blank'>Successful request ↗</a>
<a class='btn alt' href='/api/slow?ms=600' target='_blank'>Slow trace ↗</a>
<a class='btn' href='/api/fail' target='_blank'>Expected 503 failure ↗</a>
<p>Use the scripted drill to send enough failures to fire the Prometheus alert.</p></div>
<div class='card'><h2>2. Inspect telemetry</h2>
<p><a href='http://localhost:3000/d/capstone2-overview' target='_blank'>Grafana dashboard</a> ·
<a href='http://localhost:9090/alerts' target='_blank'>Prometheus alerts</a> ·
<a href='/metrics' target='_blank'>Metrics endpoint</a> · <a href='/runbook' target='_blank'>Incident runbook</a></p>
<p>Expected log labels: <code>service=demo-api</code> and <code>level=ERROR</code>.
Use Grafana Explore → Tempo to search for a request trace.</p></div>
<small>Local learning demo. The failure endpoint is deliberately unsafe and must not be deployed publicly.</small>
</main></body></html>"""


if __name__ == "__main__":
    log_event("INFO", "demo_api_started", port=8000)
    app.run(host="0.0.0.0", port=8000, threaded=True)
