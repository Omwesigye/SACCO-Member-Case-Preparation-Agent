# System & Project Requirements

This document outlines the software, environment, runtime dependencies, and configuration required to clone, install, test, and run the **SACCO Member Case Preparation Agent**.

---

## 1. System Prerequisites

| Component | Minimum Requirement | Recommended | Notes |
|---|---|---|---|
| **Operating System** | Windows 10/11, Ubuntu 20.04+, macOS 12+ | Windows 11 / Ubuntu 22.04 | Cross-platform compatible |
| **Python Runtime** | Python 3.10.x | Python 3.10.10 or 3.11.x | Verified on 3.10.10 (Local) and 3.11 (Devcontainer) |
| **Package Manager** | `pip` (v22.0+) | Latest `pip` | Included with Python installation |
| **Version Control** | Git 2.30+ | Latest Git | For repository cloning and release tagging |
| **Hardware** | 2-core CPU, 4 GB RAM | 4-core CPU, 8 GB RAM | Local TF-IDF retrieval and test execution are lightweight |
| **Network** | Internet connection | Broadband | Required only for installing dependencies and calling the Gemini API |

---

## 2. Python Package Dependencies

All primary dependencies are listed in [requirements.txt](file:///c:/Users/USER/OneDrive/Desktop/SACCO%20PROJECT/SACCO-Member-Case-Preparation-Agent/requirements.txt):

| Package | Minimum Version | Purpose |
|---|---|---|
| **`streamlit`** | `>=1.30.0` | Interactive web dashboard and loan officer demonstration UI |
| **`google-genai`** | `>=0.1.0` | Google Gemini API SDK for RAG synthesis and structured case drafting |
| **`python-dotenv`** | `>=1.0.0` | Loads environment variables securely from `.env` |
| **`pyyaml`** | `>=6.0` | Ingestion and parsing of YAML frontmatter in policy documents |
| **`scikit-learn`** | `>=1.3.0` | TF-IDF vectorization and sublinear cosine similarity retrieval |
| **`pytest`** | `>=8.0.0` | Automated test runner for the 44-case regression and guardrail suite |

*Note: The deterministic financial calculation engine relies on Python's built-in `decimal` module (`Decimal`, `ROUND_HALF_UP`) to ensure exact arithmetic precision without floating-point errors.*

---

## 3. Environment & Credentials Configuration

The system is designed with safety and offline capability in mind:
- **Offline / Local Execution:** The 44 automated tests (`pytest`) and the CLI workflow demos do **not** require an external API key or network connection.
- **Interactive UI (Streamlit):** Requires a valid Google Gemini API key to run grounded LLM generation.

### Setting Up Environment Variables:
1. Locate the [.env.example](file:///c:/Users/USER/OneDrive/Desktop/SACCO%20PROJECT/SACCO-Member-Case-Preparation-Agent/.env.example) file in the root directory.
2. Copy it to `.env`:
   - **Windows (PowerShell):** `copy .env.example .env`
   - **Linux / macOS:** `cp .env.example .env`
3. Edit `.env` and specify your Google Gemini API key:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```
   *(Get an API key at [Google AI Studio](https://aistudio.google.com/)).*

> [!SECURITY NOTE]
> Never commit your `.env` file or real API keys to version control. The repository's `.gitignore` explicitly excludes `.env`.

---

## 4. Step-by-Step Installation Guide

### Option A: Windows (PowerShell)

```powershell
# 1. Clone the repository
git clone https://github.com/Omwesigye/SACCO-Member-Case-Preparation-Agent.git
cd SACCO-Member-Case-Preparation-Agent

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env
# Edit .env with your Gemini API key if testing the Streamlit UI
```

### Option B: Linux / macOS (Bash / Zsh)

```bash
# 1. Clone the repository
git clone https://github.com/Omwesigye/SACCO-Member-Case-Preparation-Agent.git
cd SACCO-Member-Case-Preparation-Agent

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your Gemini API key if testing the Streamlit UI
```

---

## 5. Verification & Testing

Verify that your environment is properly configured by running the full automated test suite:

```bash
python -m pytest tests -v
```

**Expected Outcome:**
- **44 passed** tests across 4 test modules:
  - `tests/test_guardrails.py` (12 tests: injection awareness, auth, iteration limits)
  - `tests/test_persistent_memory.py` (7 tests: multi-turn continuity & safety invariants)
  - `tests/test_rag_pipeline.py` (7 tests: chunking, indexing, grounding, citations)
  - `tests/test_tools_orchestration.py` (18 tests: authorization, calculations, error handling)

---

## 6. How to Run the Application

### 1. Interactive Web Application (Streamlit)
*Requires `GEMINI_API_KEY` in `.env`*
```bash
streamlit run evidence/demo/sacco_baseline/app.py
```
Opens in your browser at `http://localhost:8501`.

### 2. Standalone Agent Workflow Scenarios (CLI)
*Runs locally without an API key*
```bash
cd src/agent
python run_demo.py
```
Executes three pre-configured synthetic member scenarios:
- `SACCO-M-001`: Complete case ending in `READY_FOR_REVIEW`.
- `SACCO-M-999`: Unknown member ending in `STOPPED_INCOMPLETE`.
- `SACCO-M-002`: Missing KYC documentation ending in `STOPPED_INCOMPLETE`.

### 3. Persistent Memory Continuity Demo (CLI)
*Runs locally without an API key*
```bash
cd src/agent
python run_demo_memory.py
```
Demonstrates multi-session state persistence, checklist resumption after missing KYC is supplied, and Credit Committee immutability locking.

---

## 7. Operational & Safety Boundaries

Anyone running or evaluating this codebase should note the following architectural boundaries:
1. **Advisory Decision Support:** The system prepares case files; it **never** approves loans, disburses money, scores creditworthiness, or alters balances.
2. **Deterministic Arithmetic:** All financial numbers (reducing-balance schedules, DSR, loan limits) are generated by deterministic Python functions, not by the LLM.
3. **Synthetic Data:** All member profiles (`SACCO-M-001` through `SACCO-M-010`) are synthetic. No live PII or confidential institutional data is present in this repository.
