# Autonomous Incident RCA & Self-Healing SRE Agent

An enterprise-grade autonomous AI SRE (Site Reliability Engineering) agent that diagnoses live production outages, correlates multi-service telemetry, identifies root-cause commits in Git, verifies diagnoses in an isolated container sandbox, and generates automated remediation patches with Human-in-the-Loop approval.

---

## 🌟 Key Capabilities

1. **Chaos / Fault Injection Engine:**
   * Simulates microservices: API Gateway, Auth Service, Payment Service, Order Service, PostgreSQL Database, and Redis.
   * Injects production outages:
     * **PostgreSQL Connection Pool Exhaustion:** Worker threads failing to release cursors.
     * **Container OOM CrashLoop (ExitCode 137):** Unbounded in-memory caching.
     * **Cascading Timeout Storm:** 30s downstream proxy read timeouts starving gateway threads.
2. **Autonomous ReAct Diagnostic Workflow:**
   * **Telemetry Anomaly Triage:** Unsupervised 3-sigma anomaly detection on Prometheus time series metrics (P99 latency, error rates, CPU/Memory).
   * **OpenTelemetry Log Correlation:** Traces fatal exceptions and stack traces across microservices.
   * **Git Deployment Correlation:** Inspects recent production commit histories and authors.
   * **Container Sandbox Verification:** Executes non-destructive diagnostic terminal commands (`pg_stat_activity`, `ps aux`, `cgroup` inspection).
3. **Automated Remediation & Safeguards:**
   * Synthesizes formal incident post-mortems with root cause analysis.
   * Produces production `git diff` patches.
   * **Human-in-the-Loop Safeguard:** Review and deploy or reject patch directly from the UI.

---

## 🏗️ Project Structure

```
autonomous_sre_agent/
├── data/
│   └── mock_environment/              # Telemetry simulator & generated logs/metrics
│       ├── simulator.py                # Microservice telemetry generator & chaos injector
│       ├── prometheus_metrics.csv      # Time-series Prometheus metrics
│       └── opentelemetry_logs.csv      # Distributed system logs
├── src/
│   ├── __init__.py
│   ├── agent.py                       # Multi-step ReAct autonomous SRE agent
│   └── tools/
│       ├── __init__.py
│       └── sre_tools.py               # Tool definitions (query_logs, metric_spikes, git, sandbox)
├── app/
│   └── streamlit_app.py               # Interactive Incident War Room dashboard
├── requirements.txt                   # Dependencies
└── README.md                          # Documentation
```

---

## 🚀 Quickstart Guide (Local Setup & Run)

### 1. Navigate to Project & Create Environment
Open PowerShell or your terminal:

```powershell
cd C:\Users\soumili\Desktop\projects\autonomous_sre_agent
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Launch the Incident War Room Dashboard
```powershell
streamlit run app/streamlit_app.py
```
Open your browser at `http://localhost:8501`.

---

## 🖥️ How to Test It in the Dashboard

1. **Inject Chaos (Sidebar):**
   * Choose a scenario (e.g. *PostgreSQL Connection Pool Exhaustion* or *Unbounded Cache JVM/Node OOM*).
   * Click **"⚡ Inject Fault"**.
2. **Observe War Room Triage:**
   * See the fleet health badge flip to **CRITICAL P0 INCIDENT** with red status indicators across affected services.
3. **Trigger the Autonomous Agent:**
   * Go to **"🧠 SRE Agent Autonomous RCA & Patch"** tab.
   * Click **"🚀 Trigger Autonomous Investigation"**.
   * Watch the agent work through its 5-phase ReAct audit trace.
   * Review the executive post-mortem, culprit Git commit, and the generated `git diff` patch.
4. **Deploy Self-Healing Fix:**
   * Click **"✅ Approve & Deploy Remediation to Production"** to clear the incident and restore fleet health.
