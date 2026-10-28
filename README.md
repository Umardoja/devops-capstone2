# DevOps Capstone 2 — Ship It and Keep It Running

**Beginner-friendly observability + incident response demonstration**

A working local stack for **metrics, logs, traces, alerting, dashboards, SLO and postmortem documentation**, launched with one Docker Compose command.

> **Important scope note:** This repo demonstrates Capstone 2 requirements visible in the supplied handout extract. It is **Docker Compose**, not Kubernetes/Helm/Terraform. If your instructor explicitly requires a Kubernetes deployment, ask before claiming those requirements are fulfilled. Runtime success/screenshots need to be verified on your machine.

## Quickstart (Windows, Mac, Linux)

**Prerequisites:** Docker Desktop (with Linux containers and Docker Compose v2), Python 3, at least 4–6 GB free RAM for the stack.

```bash
# 1. In the extracted project folder:
docker compose up -d --build

# 2. Check all containers
docker compose ps

# 3. Verify HTTP backends, after containers have started
python scripts/check.py

# 4. Generate real telemetry and verify alert
python scripts/drill.py
```

On Windows, PowerShell works with these same commands (`py scripts/drill.py` if `python` is not on PATH). First startup downloads several images; the time depends on internet speed. Keep Docker Desktop running.

## Local URLs

| Interface | Link | Instructions |
|---|---|---|
| Demo API | http://localhost:8000 | Interactive links to healthy/slow/failure requests |
| Grafana | http://localhost:3000 | `admin` / `localdemo123` (change via `.env` before deployment) |
| Dashboard | http://localhost:3000/d/capstone2-overview | Auto-provisioned JSON dashboard |
| Prometheus alerts | http://localhost:9090/alerts | Look for **DemoAPIHighErrorRate** in **Firing** |
| Prometheus targets | http://localhost:9090/targets | The `demo-api` target should show **UP** |
| Runbook | http://localhost:8000/runbook | Linked in Prometheus alert annotations |

## How to demonstrate each must-have

1. **Dashboard exported as code:** `grafana/dashboards/capstone2.json`, automatically loaded via Grafana provisioning at startup. No manual import.
2. **Logging config:** `fluent-bit/fluent-bit.conf` tails structured JSON log lines; Loki stores them. Use Grafana → **Explore** → **Loki** and execute:

   ```logql
   {service="demo-api",level="ERROR"}
   ```

   For all service logs use `{service="demo-api"}`. Empty? Run the drill and widen the selected time window to the last 15 minutes.

3. **Tracing config:** Flask emits OpenTelemetry spans over OTLP HTTP to `otel-collector`, which forwards to `tempo`. Open Grafana → **Explore** → select **Tempo**. Paste a trace ID printed by the drill or returned as the `X-Trace-ID` response header. Inspect root HTTP span and nested `simulated_database_call` / `simulated_dependency_failure` span.
4. **Alert fires:** `python scripts/drill.py` sends 10 expected HTTP 503s and polls Prometheus until the alert is truly **Firing**. Screenshot the page `http://localhost:9090/alerts` immediately when it fires; the simulated failure alert automatically clears after its one-minute rolling window passes.
5. **Runbook linked:** Open the `runbook_url` field of the firing alert. This points to `http://localhost:8000/runbook`.
6. **SLO and error budget:** See [`docs/SLO_AND_ERROR_BUDGET.md`](docs/SLO_AND_ERROR_BUDGET.md).
7. **Blameless postmortem:** Complete the real incident times in [`docs/BLAMELESS_POSTMORTEM.md`](docs/BLAMELESS_POSTMORTEM.md) after performing the drill.

## Source and evidence files

- `docker-compose.yml` — all service definitions.
- `app/server.py` — demo API, Prometheus metrics, structured logging, OpenTelemetry tracing.
- `prometheus/alerts.yml` — runbook-linked high-error and down alert rules.
- `grafana/dashboards/capstone2.json` — dashboard-as-code with success %, latency, logs, requests.
- `fluent-bit/` — centralized JSON logs to Loki, indexed by service and level.
- `otel-collector/` and `tempo/` — end-to-end trace pipeline.
- `docs/ARCHITECTURE.md` — diagram and signal flow.
- `docs/RUNBOOK.md` — alert response instructions.
- `docs/SLO_AND_ERROR_BUDGET.md` — 99% success target and 1% failure allowance.
- `docs/BLAMELESS_POSTMORTEM.md` — complete with genuine incident observations.
- `docs/SUBMISSION_CHECKLIST.md` — maps deliverables to grading.
- `docs/DEMO_SCRIPT.md` — concise presentation script.
- `screenshots/` — save actual Grafana, Prometheus, Loki and Tempo screenshots here.

## Diagnostics

```bash
docker compose ps
docker compose logs --tail=80 demo-api prometheus
docker compose logs --tail=80 fluent-bit loki otel-collector tempo
docker compose logs --tail=80 grafana
```

If the chart is empty: send some requests (`python scripts/drill.py`), make sure Prometheus target is UP, and set the Grafana time range to **Last 15 minutes**.

If Loki logs are missing: ensure `runtime/logs/app.jsonl` exists and has JSON request lines, then check `docker compose logs fluent-bit` for Loki ingest errors.

If Tempo traces are missing: wait 5–15 seconds for batch export, check the `X-Trace-ID` header and `docker compose logs otel-collector tempo demo-api`.

If `3000`, `8000`, `9090`, `3100`, or `3200` is already in use: stop the conflicting local process before launching the stack.

To stop: `docker compose down`. To delete retained test data **permanently**: `docker compose down -v`.

## Safety, limitations and production follow-up

- All published ports are bound to `127.0.0.1`, not to a public network.
- Demo Grafana credentials are documented for local use only. For any other use, set `GRAFANA_ADMIN_PASSWORD` in a private `.env` file and configure access controls/TLS.
- Failure injection and trace IDs are for demonstration only. Do not expose this service publicly.
- This setup has no external notifications, production durable object storage, Kubernetes deployment, or validated 30-day SLO. Those are future improvements, not claims in this submission.
- Local 30-day compliance cannot be established from demo metrics because Prometheus retention here is three days.

## Further reading

- Grafana documentation on provisioning: https://grafana.com/docs/grafana/latest/administration/provisioning/
- Loki local config examples: https://grafana.com/docs/loki/latest/configure/examples/configuration-examples/
- Grafana Tempo examples: https://grafana.com/docs/tempo/latest/docker-example/
