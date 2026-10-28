"""Exercise successful requests, a trace, an incident and the Prometheus alert."""
import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

APP = "http://localhost:8000"
PROM = "http://localhost:9090"


def get(url, timeout=4):
    try:
        with urlopen(url, timeout=timeout) as res:
            return res.status, res.headers.get("X-Trace-ID", ""), res.read().decode()
    except HTTPError as error:
        return error.code, error.headers.get("X-Trace-ID", ""), error.read().decode()


def main():
    print("CHECK 1/4: connecting to application")
    try:
        print("  health:", get(APP + "/healthz")[2])
    except (URLError, OSError) as e:
        raise SystemExit(f"Application not reachable: {e}. Run docker compose up -d --build")
    print("CHECK 2/4: sending healthy and slow traced requests")
    for _ in range(15):
        get(APP + "/api/ok")
    status, trace_id, _ = get(APP + "/api/slow?ms=450")
    print("  slow request:", status, "trace ID:", trace_id)
    print("CHECK 3/4: injecting ten intentional failures")
    for _ in range(10):
        status, _, _ = get(APP + "/api/fail")
        if status != 503:
            print("  WARNING: expected HTTP 503, saw", status)
    print("CHECK 4/4: waiting for alert DemoAPIHighErrorRate to FIRE")
    for iteration in range(24):
        time.sleep(5)
        try:
            data = json.loads(get(PROM + "/api/v1/alerts")[2])
            for alert in data.get("data", {}).get("alerts", []):
                if alert.get("labels", {}).get("alertname") == "DemoAPIHighErrorRate":
                    print("  Prometheus status:", alert.get("state"))
                    if alert.get("state") == "firing":
                        print("SUCCESS: alert fired. Take screenshot now: http://localhost:9090/alerts")
                        print("Logs: Grafana Explore → Loki → {service=\"demo-api\", level=\"ERROR\"}")
                        print("Traces: Grafana Explore → Tempo; search service.name=demo-api")
                        print("Known trace ID:", trace_id)
                        return
        except (URLError, OSError, ValueError) as error:
            print("  Prometheus not ready:", error)
    raise SystemExit("Alert did not fire in time. Check `docker compose logs prometheus` and check target is UP.")


if __name__ == "__main__":
    main()
