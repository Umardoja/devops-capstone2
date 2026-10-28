# Incident Runbook — High Error Rate

**Alert name:** DemoAPIHighErrorRate

**Severity:** Critical (classroom drill)

**Service:** demo-api

**Expected condition:** More than 3 HTTP 5xx responses in a rolling 1-minute interval.

## 1. Confirm alert
Open http://localhost:9090/alerts and locate **DemoAPIHighErrorRate**. Confirm state is **FIRING**. Do not mistake **Inactive** or **Pending** for firing.

## 2. Inspect metrics
Open http://localhost:3000/d/capstone2-overview. Check the red/5xx request count and success rate. Use Prometheus to run:

`sum(increase(http_requests_total{status=~"5.."}[1m]))`

## 3. Inspect error logs
Open Grafana → Explore → select **Loki** → run:

`{service="demo-api",level="ERROR"}`

Review fields `route`, `status`, `message`, and `trace_id`.

## 4. Investigate trace
Copy the `trace_id` field from a request log or the HTTP `X-Trace-ID` header. Open Grafana → Explore → **Tempo**, search or paste the trace ID. Inspect the root HTTP request span and the nested dependency failure span.

## 5. Mitigate and recover
Stop hitting `/api/fail`. Send good requests with `python scripts/drill.py` only when intentionally repeating the incident; otherwise use `python -c "import urllib.request; [urllib.request.urlopen('http://localhost:8000/api/ok').read() for _ in range(20)]"`.

The alert uses a one-minute lookback and will eventually return to Inactive once error samples age out of the window. If the API has stopped, run `docker compose ps` and `docker compose logs demo-api`, then `docker compose up -d` if necessary.

## 6. Document event without assigning blame
Record what failed, the user impact, timeline, how monitoring detected it, how it was mitigated, and practical prevention work. Use `docs/BLAMELESS_POSTMORTEM.md`.
