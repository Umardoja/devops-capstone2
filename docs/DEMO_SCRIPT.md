# 90-second demo script

**0–15s:** Open `http://localhost:8000`. “This is a small demo API with metrics, logs, and traces. It includes one intentionally failing route to test alerting safely.”

**15–30s:** Open `http://localhost:3000/d/capstone2-overview`. “This dashboard was automatically loaded from a committed JSON file. Prometheus collects our HTTP success rate, latency and error counts.”

**30–45s:** Run `python scripts/drill.py`. “This script sends successful requests, one slower traced request, then intentional 503 errors.”

**45–60s:** Open `http://localhost:9090/alerts` when the script says Firing. “Prometheus detects over three 5xx responses within a minute and fires the alert. The alert has a runbook link.”

**60–75s:** Grafana → Explore → Loki → `{service="demo-api",level="ERROR"}`. “Logs are searchable by service and severity, and include the trace ID.”

**75–90s:** Grafana → Explore → Tempo → paste a trace ID from `X-Trace-ID` or script output. “The trace shows nested spans and the simulated dependency failure. The SLO defines 99% request success with 1% error budget.”
