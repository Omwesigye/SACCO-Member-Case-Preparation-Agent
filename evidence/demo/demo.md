# Demonstration Evidence & Run Guide

This directory houses the interactive application artifacts and demonstration guides for the **SACCO Member Case Preparation Agent**.

Per the Week 8 capstone deliverables:
> *"Working live presentation/demonstration showing problem, progression, successful workflow, evidence view, failure handling, and guardrails."*

---

## 1. Live Cloud Deployment

The baseline system is deployed and publicly accessible online:

- **Streamlit Cloud URL:**  
  [https://sacco-member-case-preparation-agent-bzbryaduwvsuifpyzbu5fx.streamlit.app/](https://sacco-member-case-preparation-agent-bzbryaduwvsuifpyzbu5fx.streamlit.app/)

The web application allows loan officers to:
1. Select from 10 synthetic member profiles (`SACCO-M-001` through `SACCO-M-010`).
2. Run automated policy retrieval against the 20 SACCO policy documents.
3. Compute exact reducing-balance repayment schedules and debt ratios using deterministic Python functions.
4. Synthesize a structured case brief with source citations.
5. Review policy checks, affordability flags, and human handover actions before submission.

---

## 2. Running the Demo Locally

### Interactive Streamlit UI
*Requires a valid `GEMINI_API_KEY` set in your `.env` file.*

```bash
streamlit run evidence/demo/sacco_baseline/app.py
```
Access the application at `http://localhost:8501`.

### Standalone CLI Scenarios Demo
*Does not require any API key or external service.*

```bash
cd src/agent
python run_demo.py
```
This script exercises 3 core workflows and outputs structured traces to `src/agent/execution_traces.txt`.

### Multi-Session Persistent Memory Demo
*Does not require any API key.*

```bash
cd src/agent
python run_demo_memory.py
```
Demonstrates safe multi-session state resumption and Credit Committee finality locking.
