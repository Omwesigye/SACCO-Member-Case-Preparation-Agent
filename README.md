# SACCO Member Case Preparation Agent

A bounded AI agent that helps SACCO loan officers prepare member cases for review. It retrieves relevant clauses from a controlled corpus of SACCO policy documents (RAG), reads a **synthetic** member record, runs a **deterministic** repayment calculator, and assembles a structured case brief.

**Human control:** the agent never approves loans, disburses funds or changes accounts. Every case ends as a draft for human review (`READY_FOR_REVIEW`, or `STOPPED_INCOMPLETE` when evidence or data is missing). All financial figures come from tested code, not from the language model. All member data is synthetic.

See the full [Project Charter](docs/project-charter.md).

## Repository layout

| Path | Contents |
|---|---|
| `RAG/` | Policy corpus (20 documents) plus `source_register.md` with provenance |
| `src/rag/` | Ingestion, retriever and grounded pipeline with citations |
| `src/agent/` | Orchestrator, tools, case memory, tracing, and demo scripts |
| `Tools/` | Member-record tool, repayment calculator, orchestration layer, tool catalogue |
| `tests/` | Automated tests (RAG, guardrails, persistent memory, tool orchestration) |
| `docs/` | Architecture, requirements, evaluation, and weekly reports |
| `evidence/` | Demo app, screenshots and traces |

Architecture: [docs/architecture/architecture.md](docs/architecture/architecture.md) and [agent contract](docs/architecture/agent_contract.md).

## Prerequisites
- Python 3.10 or newer (the test suite was verified on Python 3.10.10; the devcontainer uses 3.11)
- A Gemini API key. This is needed only for the Streamlit demo, which uses `GEMINI_API_KEY`. The tests and the CLI demo do not need a key.

## Setup

Windows (PowerShell):
```powershell
git clone https://github.com/Omwesigye/SACCO-Member-Case-Preparation-Agent
cd SACCO-Member-Case-Preparation-Agent
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Linux / macOS:
```bash
git clone https://github.com/Omwesigye/SACCO-Member-Case-Preparation-Agent
cd SACCO-Member-Case-Preparation-Agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then edit `.env` and set `GEMINI_API_KEY` to your key.

## Run

### 1. Streamlit demo (needs `GEMINI_API_KEY`)
```bash
streamlit run evidence/demo/sacco_baseline/app.py
```
It opens at http://localhost:8501.

### 2. CLI agent scenarios (no API key needed)
Run from inside `src/agent`, because the scripts use local imports:
```bash
cd src/agent
python run_demo.py
```
This runs three synthetic scenarios and writes `execution_traces.txt`:

| Member | Scenario | Final status |
|---|---|---|
| `SACCO-M-001` | Complete, well-formed case | `READY_FOR_REVIEW` |
| `SACCO-M-999` | Member not found | `STOPPED_INCOMPLETE` |
| `SACCO-M-002` | KYC missing | `STOPPED_INCOMPLETE` |

### 3. Persistent-memory demo
```bash
cd src/agent
python run_demo_memory.py
```
A multi-session demo of safe case memory (an incomplete case is resumed once KYC arrives).

## Tests
From the repository root:
```bash
python -m pytest tests -v
```
Verified result: 44 passed. RAG test details are in [tests/tests.md](tests/tests.md).

## Logs and traces
- Execution traces: `execution_traces.txt` (created by `run_demo.py`)
- Observability events and traces: `src/agent/output/agent_events.jsonl` and `agent_traces.jsonl`
- Case memory: `src/agent/storage/`

## Evaluation and known limitations
- Evaluation: [docs/evaluation/](docs/evaluation/)
- Known failure modes: [docs/evaluation/failure-catalogue.md](docs/evaluation/failure-catalogue.md)
- The corpus and member records are synthetic or team-authored. This is a prototype, not a production financial system.

## Reports
Weekly and final engineering reports are in [docs/weekly-reports/](docs/weekly-reports/).

## Team
| Name | Role |
|---|---|
| Naluyinda Moureen | DevOps and Documentation lead |
| Mpirirwe Moses | Quality and Security lead |
| Nsubuga Collins | Applications and Integration lead |
| Ainembabazi Britah | AI Engineering lead |
| Omwesigye Seezi | Projects and Requirements lead |
