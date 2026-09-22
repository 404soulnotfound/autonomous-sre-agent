"""
Diagnostic Tools for the Autonomous SRE Agent.
Provides tool-calling functions:
1. query_logs(service, level, keyword, limit)
2. get_prometheus_metric_spikes(metric_name, threshold_pct)
3. inspect_git_commits(service, limit)
4. execute_diagnostic_sandbox_command(command)
"""

import pandas as pd
import numpy as np
from pathlib import Path


class SRETools:
    GIT_COMMITS = [
        {"hash": "7a8f9c2", "service": "payment-service", "author": "dev-alex", "message": "feat(payment): batch settlement processing without explicit cursor disposal", "age": "45m ago"},
        {"hash": "9c104e1", "service": "api-gateway", "author": "dev-sara", "message": "chore(deps): bump rate-limiter package", "age": "2h ago"},
        {"hash": "3b1e5a4", "service": "order-service", "author": "dev-marcus", "message": "perf(order): in-memory memoization of order histories", "age": "1h ago"},
        {"hash": "f90c21b", "service": "api-gateway", "author": "dev-kevin", "message": "chore(gateway): increase proxy read timeout to 30s", "age": "30m ago"},
        {"hash": "881a29f", "service": "auth-service", "author": "dev-sara", "message": "refactor(jwt): rotate public signing keys", "age": "5h ago"}
    ]

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)

    def query_logs(self, service: str = None, level: str = None, keyword: str = None, limit: int = 15) -> list[dict]:
        """Queries OpenTelemetry logs based on service, log severity level, or error text."""
        log_file = self.data_dir / "opentelemetry_logs.csv"
        if not log_file.exists():
            return []
            
        df = pd.read_csv(log_file)
        if service and service != "all":
            df = df[df["service"] == service]
        if level and level != "all":
            df = df[df["level"] == level.upper()]
        if keyword:
            df = df[df["message"].str.contains(keyword, case=False, na=False)]
            
        return df.head(limit).to_dict(orient="records")

    def get_prometheus_metric_spikes(self, metric_name: str = "latency_p99_ms", std_multiplier: float = 2.5) -> list[dict]:
        """Runs unsupervised 3-sigma anomaly detection on Prometheus time series metrics."""
        metric_file = self.data_dir / "prometheus_metrics.csv"
        if not metric_file.exists():
            return []
            
        df = pd.read_csv(metric_file)
        if metric_name not in df.columns:
            return []
            
        anomalies = []
        for svc, group in df.groupby("service"):
            vals = group[metric_name].values
            mean_val = np.mean(vals)
            std_val = np.std(vals)
            latest_val = vals[-1]
            
            # Check if current value exceeds threshold
            z_score = (latest_val - mean_val) / max(std_val, 1e-4)
            if z_score > std_multiplier:
                anomalies.append({
                    "service": svc,
                    "metric": metric_name,
                    "baseline_mean": round(float(mean_val), 1),
                    "current_value": round(float(latest_val), 1),
                    "z_score": round(float(z_score), 2),
                    "status": "SPIKING ANOMALY"
                })
        return anomalies

    def inspect_git_commits(self, service: str = None, limit: int = 5) -> list[dict]:
        """Inspects recent Git commits deployed to production in the last 4 hours."""
        if service and service != "all":
            filtered = [c for c in self.GIT_COMMITS if c["service"] == service]
            return filtered[:limit]
        return self.GIT_COMMITS[:limit]

    def execute_diagnostic_sandbox_command(self, command: str) -> dict:
        """Executes a diagnostic command within the virtual mock container sandbox."""
        cmd = command.strip().lower()
        if "pg_stat_activity" in cmd or "psql" in cmd:
            return {
                "exit_code": 0,
                "output": "datname | usename | client_addr | state  | waiting | query_duration\n"
                          "orders  | app_usr | 10.0.1.42   | active | t       | 00:04:12\n"
                          "orders  | app_usr | 10.0.1.42   | idle in transaction | t | 00:08:45\n"
                          "[ALERT] 98/100 active connections in state 'idle in transaction' holding locks."
            }
        elif "top" in cmd or "ps aux" in cmd or "memory" in cmd:
            return {
                "exit_code": 0,
                "output": "PID   USER     %CPU %MEM   VSZ   RSS STAT START   TIME COMMAND\n"
                          "1421  node     12.1 98.4 4891M 3982M Sl+  04:15   1:12 node /app/order_service.js\n"
                          "[WARN] Process RSS exceeding container cgroup memory limits (Hard limit: 4096M)."
            }
        elif "curl" in cmd or "ping" in cmd or "timeout" in cmd:
            return {
                "exit_code": 1,
                "output": "HTTP/1.1 504 Gateway Timeout\nConnection: keep-alive\n"
                          "curl: (28) Operation timed out after 30001 milliseconds with 0 bytes received."
            }
        else:
            return {
                "exit_code": 0,
                "output": f"Sandbox diagnostic completed. Status healthy for command: `{command}`"
            }
