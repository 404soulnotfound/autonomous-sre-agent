"""
Mock Microservice Production Cloud Environment & Telemetry Simulator.
Simulates a distributed architecture:
- API Gateway (Kong / Envoy)
- Auth Service
- Payment Service
- Order Processing Service
- PostgreSQL Database
- Redis Cache Cluster

Supports Fault Injections:
1. DB Connection Pool Exhaustion (Caused by a bad query in recent commit)
2. Memory Leak / OOM CrashLoop (Caused by unbounded caching)
3. Microservice Latency Cascade / Timeout Storm (Downstream API rate limit)
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path


class MockCloudEnvironment:
    SERVICES = ["api-gateway", "auth-service", "order-service", "payment-service", "postgres-db", "redis-cache"]
    
    FAULT_SCENARIOS = {
        "db_connection_leak": {
            "title": "PostgreSQL Connection Pool Exhaustion",
            "trigger_service": "payment-service",
            "root_cause": "Commit 7a8f9c2 omitted conn.close() in process_settlement() worker thread.",
            "culprit_commit": "7a8f9c2: feat(payment): batch settlement processing without explicit cursor disposal",
            "affected_services": ["payment-service", "postgres-db", "order-service"],
            "suggested_patch": "diff --git a/services/payment/db.py b/services/payment/db.py\n@@ -42,3 +42,5 @@\n+    finally:\n+        conn.close() # Return connection to pool"
        },
        "memory_leak_oom": {
            "title": "Unbounded Cache JVM/Node OOM CrashLoop",
            "trigger_service": "order-service",
            "root_cause": "Order payload caching dict grew monotonically without TTL eviction policy.",
            "culprit_commit": "3b1e5a4: perf(order): in-memory memoization of order histories",
            "affected_services": ["order-service", "api-gateway"],
            "suggested_patch": "diff --git a/services/order/cache.py b/services/order/cache.py\n@@ -15,2 +15,3 @@\n-cache = {}\n+from cachetools import TTLCache\n+cache = TTLCache(maxsize=10000, ttl=300)"
        },
        "downstream_timeout_storm": {
            "title": "Payment Gateway Timeout Cascade & Thread Starvation",
            "trigger_service": "api-gateway",
            "root_cause": "Missing circuit breaker pattern; 30s timeout on 3rd party bank webhook starved gateway threads.",
            "culprit_commit": "f90c21b: chore(gateway): increase proxy read timeout to 30s",
            "affected_services": ["api-gateway", "payment-service"],
            "suggested_patch": "diff --git a/gateway/nginx.conf b/gateway/nginx.conf\n@@ -28,2 +28,3 @@\n-proxy_read_timeout 30s;\n+proxy_read_timeout 3s;\n+proxy_next_upstream error timeout http_502;"
        }
    }

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.active_fault = None
        self.logs = []
        self.metrics = []

    def inject_fault(self, scenario_key: str):
        if scenario_key not in self.FAULT_SCENARIOS:
            raise ValueError(f"Unknown scenario {scenario_key}")
        self.active_fault = scenario_key
        self.generate_telemetry()
        return self.FAULT_SCENARIOS[scenario_key]

    def clear_fault(self):
        self.active_fault = None
        self.generate_telemetry()

    def generate_telemetry(self, n_points: int = 120):
        """
        Generates 120 minutes of time-series Prometheus metrics and OpenTelemetry logs.
        """
        now = datetime.now()
        base_time = now - timedelta(minutes=n_points)
        
        metrics_list = []
        logs_list = []
        
        fault_info = self.FAULT_SCENARIOS.get(self.active_fault) if self.active_fault else None
        
        for i in range(n_points):
            t_stamp = base_time + timedelta(minutes=i)
            t_str = t_stamp.strftime("%Y-%m-%d %H:%M:%S")
            
            is_fault_active = (self.active_fault is not None) and (i >= 70)  # fault starts at minute 70
            
            for svc in self.SERVICES:
                # Default baseline health metrics
                cpu = np.random.uniform(15, 35)
                memory = np.random.uniform(40, 55)
                error_rate = np.random.uniform(0.01, 0.05)
                latency_p99 = np.random.uniform(45, 95)
                active_conns = np.random.randint(10, 30)

                # Fault injection distortions
                if is_fault_active:
                    if self.active_fault == "db_connection_leak":
                        if svc == "postgres-db":
                            active_conns = min(100, int(30 + (i - 70) * 1.6))
                            cpu = min(98, 30 + (i - 70) * 1.2)
                            if active_conns >= 95:
                                logs_list.append({
                                    "timestamp": t_str, "service": svc, "level": "FATAL",
                                    "message": "FATAL: remaining connection slots are reserved for non-replication superuser connections (max_connections=100)"
                                })
                        elif svc == "payment-service":
                            latency_p99 = min(5000, 80 + (i - 70) * 85)
                            error_rate = min(0.65, 0.05 + (i - 70) * 0.015)
                            logs_list.append({
                                "timestamp": t_str, "service": svc, "level": "ERROR",
                                "message": f"ConnectionAcquisitionTimeoutError: Failed to obtain DB connection from pool after 30000ms. Active workers: 64"
                            })
                    elif self.active_fault == "memory_leak_oom":
                        if svc == "order-service":
                            memory = min(99.5, 45 + (i - 70) * 1.3)
                            if memory > 92:
                                error_rate = min(0.85, 0.1 + (i - 70) * 0.02)
                                logs_list.append({
                                    "timestamp": t_str, "service": svc, "level": "CRITICAL",
                                    "message": f"KubeletEvent: Container order-service-worker OOMKilled. ExitCode: 137. RestartCount: {int((i-70)//3)}"
                                })
                    elif self.active_fault == "downstream_timeout_storm":
                        if svc in ["api-gateway", "payment-service"]:
                            latency_p99 = min(12000, 100 + (i - 70) * 220)
                            error_rate = min(0.55, 0.02 + (i - 70) * 0.012)
                            logs_list.append({
                                "timestamp": t_str, "service": svc, "level": "WARN",
                                "message": f"UpstreamTimeout: HTTP 504 Gateway Timeout on POST /api/v1/payments. Downstream bank cluster unresponsive."
                            })

                metrics_list.append({
                    "timestamp": t_str,
                    "service": svc,
                    "cpu_usage_pct": round(cpu, 1),
                    "memory_usage_pct": round(memory, 1),
                    "error_rate_pct": round(error_rate * 100, 2),
                    "latency_p99_ms": round(latency_p99, 1),
                    "active_connections": active_conns
                })
                
                # Normal background logs
                if np.random.rand() < 0.05:
                    logs_list.append({
                        "timestamp": t_str, "service": svc, "level": "INFO",
                        "message": f"Healthcheck 200 OK. Processed batch {np.random.randint(100, 999)} transactions."
                    })

        self.metrics_df = pd.DataFrame(metrics_list)
        self.logs_df = pd.DataFrame(logs_list).sort_values("timestamp", ascending=False)
        
        # Save to disk
        self.metrics_df.to_csv(self.data_dir / "prometheus_metrics.csv", index=False)
        self.logs_df.to_csv(self.data_dir / "opentelemetry_logs.csv", index=False)


if __name__ == "__main__":
    env = MockCloudEnvironment(Path(__file__).resolve().parent / "mock_environment")
    env.inject_fault("db_connection_leak")
    print(f"[+] Initialized mock environment with telemetry at: {env.data_dir}")
