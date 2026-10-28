# Blameless Postmortem — Controlled Dependency Failure Drill

**Date:** 28 October 2026  
**Service:** `demo-api`  
**Incident type:** Intentionally injected lab failures; not a real production outage  
**Severity:** Simulation only  
**Status:** Detection verified; automatic clearing after the rolling-window period was not separately captured

## Executive summary
A planned failure drill sent ten intentionally failing requests to `/api/fail` to simulate an unavailable dependency. The demonstration application responded with HTTP 503 errors. The `DemoAPIHighErrorRate` alert changed to **Firing**, verified both by the drill script output and a Prometheus screenshot. Grafana showed an error spike, Loki returned centrally searchable JSON error logs for `demo-api`, and Tempo displayed a sampled trace containing a parent `/api/slow` request and a nested `simulated_database_call` span. This was a controlled, local demonstration; it did not impact actual customers.

## Observed timeline (only times available in screenshots)

| When | Verified observation |
|---|---|
| 2026-10-28, precise time not captured | `python scripts/drill.py` reported `Prometheus status: firing` and `SUCCESS: alert fired.` |
| 2026-10-28 20:54 UTC (timestamps within screenshot) | Loki displayed 503-related ERROR records from the simulated failure endpoint. |
| 2026-10-28, exact time not recorded | Prometheus screenshot showed `DemoAPIHighErrorRate (1 active)` with `Firing (1)`. |
| 2026-10-28, exact time not recorded | Grafana dashboard displayed an increased 5xx error rate; a rolling one-minute success rate of 0% during the failure burst, with Prometheus scrape health 1. |
| 2026-10-28 21:27:53.557 (as displayed in Grafana) | Tempo trace recorded `GET /api/slow` (200) with total duration 453.58 ms; nested `simulated_database_call` span lasted 450.22 ms. |
| 2026-10-28, after the checks | `python scripts/check.py` returned six passing checks: Application, Metrics, Prometheus, Loki, Tempo and Grafana. |

## Impact
Ten HTTP 503 responses were purposely injected by the drill, as reported by the script. No external users were involved. The success rate on the dashboard can temporarily drop to 0% because the most recent one-minute window can consist almost entirely of test failures; this is not a claim about longer-term reliability.

## Root cause
The endpoint `/api/fail` was deliberately invoked to emulate dependency unavailability. This is a synthetic test and does not imply fault or negligence by any person.

## Detection and response
- Prometheus recorded application metrics and fired `DemoAPIHighErrorRate`.
- The alert configuration provides a runbook URL: `http://localhost:8000/runbook` (local environment only).
- Fluent Bit forwarded structured application logs to Loki; Grafana could query failures by `service` and `level` labels.
- The application exported OpenTelemetry spans through the collector to Tempo; Grafana displayed the HTTP span and nested simulated operation.
- `python scripts/check.py` validated that the six checked services were reachable and ready.

## Resolution and recovery plan
The failure injection was limited to the test requests, rather than a persistent outage. Stop issuing `/api/fail` requests, verify `/api/ok` returns HTTP 200, and allow the one-minute error-rate window to clear. **The alert's return to Inactive was not documented in the provided evidence**, so this report does not claim it was observed.

## What went well
The alert fired as intended, centralized error logs were searchable, one trace included two spans, and all six readiness checks passed. Observability components were provisioned as code.

## Next improvements
- Validate and capture the alert recovery state and recovery time.
- Configure a real notification route; firing in Prometheus is verified, but external notification delivery is not part of the demonstrated evidence.
- Add longer retention, authorization, TLS and durable data storage before any public deployment.
- Consider burn-rate alerting once the system has sufficient long-term SLO history.

## Evidence
- `screenshots/01-prometheus-firing-alert.png`
- `screenshots/02-grafana-live-dashboard.png`
- `screenshots/03-loki-error-logs.png`
- `screenshots/04-tempo-trace.png`
- Local terminal result: `RESULT: 6/6 services checked` (reported by operator; screenshot not included in this bundle).
