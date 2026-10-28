# DevOps Capstone 2 — Submission Summary

**Project:** Ship It and Keep It Running — Metrics, Logs, Traces and Incident Response  
**Status:** Implemented and demonstrated locally with Docker Compose on 28 October 2026  
**Scope:** Local demonstration; not a Kubernetes/Terraform/Helm deployment

## System architecture

`demo-api` (Flask) emits Prometheus HTTP metrics, JSON logs and OpenTelemetry spans. Prometheus scrapes metrics and evaluates alert rules. Fluent Bit forwards application JSON logs to Loki. OpenTelemetry Collector receives spans and forwards them to Tempo. Grafana provides the dashboard and Explore interface for metrics, searchable logs and traces. A local runbook is linked in alert annotations.

## Deliverables

| Instructor requirement | Implementation | Evidence |
|---|---|---|
| Dashboard exported as code | `grafana/dashboards/capstone2.json` | `screenshots/02-grafana-live-dashboard.png` |
| Logging configuration | `fluent-bit/fluent-bit.conf`, `loki/config.yaml` | `screenshots/03-loki-error-logs.png` |
| Tracing configuration | `otel-collector/config.yaml`, `tempo/tempo.yaml`, `app/server.py` | `screenshots/04-tempo-trace.png` |
| SLO and error budget | `docs/SLO_AND_ERROR_BUDGET.md` | Document in repo |
| Alert fires during drill | `prometheus/alerts.yml`, `scripts/drill.py` | `screenshots/01-prometheus-firing-alert.png` |
| Searchable logs by service and level | Loki label query: `{service="demo-api",level="ERROR"}` | `screenshots/03-loki-error-logs.png` |
| One request traced | Grafana Tempo displayed `/api/slow` with 2 spans | `screenshots/04-tempo-trace.png` |
| Alert-linked runbook | `docs/RUNBOOK.md`, `runbook_url` annotation | Alert rule in repo |
| Blameless postmortem | `docs/BLAMELESS_POSTMORTEM.md` | This incident report |

## Verification performed

- `docker compose up -d --build`: completed, seven containers reported Up.
- `python scripts/check.py`: all six readiness checks passed.
- `python scripts/drill.py`: ten simulated failure requests and successful Prometheus alert firing.
- Loki Explore: 40 matching ERROR log entries visible within the selected one-hour range.
- Tempo: a 453.58 ms trace with a nested 450.22 ms simulated database span.
- Grafana dashboard: request rates, HTTP 5xx behavior, response latency, healthy scrape signal, and structured log panel visible.

## Limitations

This project uses Docker Compose rather than Kubernetes, Helm or Terraform. It demonstrates detection in Prometheus but does not demonstrate a delivered external alert notification, production-grade authentication, durable long-term retention or an achieved multi-day SLO. These would be next-phase work.

## Run locally

```bash
docker compose up -d --build
python scripts/check.py
python scripts/drill.py
```

## GitHub repository

**Repository link:** [Insert the actual public GitHub repository URL before submitting]
