"""No-extra-dependency local observability checks after Docker has started."""
import json
import sys
from urllib.error import URLError
from urllib.request import urlopen

checks = [
    ("Application health", "http://localhost:8000/healthz", "ok"),
    ("Metrics exposed", "http://localhost:8000/metrics", "http_requests_total"),
    ("Prometheus ready", "http://localhost:9090/-/ready", "ready"),
    ("Loki ready", "http://localhost:3100/ready", "ready"),
    ("Tempo ready", "http://localhost:3200/ready", "ready"),
    ("Grafana API", "http://localhost:3000/api/health", "database"),
]
errors = 0
for label, url, expected in checks:
    try:
        with urlopen(url, timeout=5) as res:
            body = res.read().decode()
        ok = expected.lower() in body.lower()
    except (URLError, OSError) as exc:
        body = str(exc)
        ok = False
    print(("PASS" if ok else "FAIL"), label, ("" if ok else body[:150]))
    if not ok:
        errors += 1
print(f"RESULT: {len(checks)-errors}/{len(checks)} services checked")
sys.exit(1 if errors else 0)
