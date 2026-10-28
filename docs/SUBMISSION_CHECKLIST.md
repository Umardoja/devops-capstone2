# Submission checklist — instructor rubric

## Working system (50%)
- [ ] `docker compose up -d --build` starts all seven services
- [ ] `python scripts/check.py` reports 6/6 checks
- [ ] `python scripts/drill.py` reports the alert reached **Firing**
- [ ] Grafana dashboard shows real traffic and failures
- [ ] Grafana Explore: Loki `{service="demo-api",level="ERROR"}` returns matching logs
- [ ] Grafana Explore: Tempo shows a real request trace with child span

## Automation and documentation (30%)
- [x] Docker Compose reproducible services
- [x] Grafana dashboard and datasource provisioning committed as code
- [x] Prometheus metrics scrape and alert rule committed
- [x] Fluent Bit structured log config + Loki backend committed
- [x] OpenTelemetry Collector config + Tempo backend committed
- [x] SLO and error budget document
- [x] Runbook linked from alert annotations
- [x] Blameless postmortem *template* (complete real drill timeline before submission)
- [x] Architecture diagram and README instructions

## Demo and Q&A (20%)
- [ ] Capture dashboard, alert, log query, trace screenshots in `screenshots/`
- [ ] Record a 60–90 second screen demo if form allows
- [ ] Push Git repository and copy link
- [ ] Fill submission form and confirm receipt

## Important honesty check
Do not mark run-time items complete or claim the alert fired unless you saw it happen. If the instructor explicitly requires Kubernetes, Helm, or Terraform, this Docker Compose version is an alternative demo and is **not** a substitute for those requirements.
