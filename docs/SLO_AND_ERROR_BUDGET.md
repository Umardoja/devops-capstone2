# SLO and Error Budget — demo-api

**Service:** `demo-api`

**User journey:** An HTTP client calls `/api/ok` or `/api/slow` and receives an HTTP response.

**SLI (service-level indicator):** Proportion of observed HTTP requests that are NOT 5xx responses. Expected 503 failures from `/api/fail` are included in the error calculation. (Monitoring traffic to `/metrics` and `/healthz` is excluded.)

**SLO (service-level objective):** At least **99.0%** of monitored HTTP requests succeed in a rolling **30-day** window.

**Error budget:** 1.0% of monitored requests can fail in 30 days.

| Example volume in 30 days | Allowed 5xx failures (1%) |
|---:|---:|
| 1,000 | 10 |
| 10,000 | 100 |
| 100,000 | 1,000 |

## PromQL used for SLI

```promql
100 * sum(rate(http_requests_total{status!~"5.."}[5m]))
    / clamp_min(sum(rate(http_requests_total[5m])), 0.000001)
```

The dashboard uses a one-minute window for an immediately visible demo; the declared 30-day SLO requires persistent 30-day metrics to assess fully. The example infrastructure retains Prometheus data for only three days, so it **does not prove 30-day compliance**.

## Demo alert and response

Rule: `DemoAPIHighErrorRate` triggers when `sum(increase(http_requests_total{status=~"5.."}[1m])) > 3`.

This is a fast demonstration alert, **not a rigorous burn-rate alert**. The threshold is intentionally low so the live drill can reach Firing within seconds. For production, add sustained multiwindow burn-rate alerting and replace the local runbook URL with a reachable documentation site.

## Policy when budget runs low

1. Investigate the failing endpoint or dependency with traces and error logs.
2. Pause risky changes when budget consumption exceeds normal levels.
3. Restore successful responses and verify the alert clears.
4. Record root causes, customer impact, detection time, and prevention actions in a blameless postmortem.
