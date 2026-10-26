# SACCO Agent Interface and Architecture Visual Evidence

**Evidence Module:** Visual Artifacts, Architectural Schemas, and Interface Walkthroughs  
**Repository Location:** `/evidence/screenshots`  
**Governing Standard:** Human-in-the-Loop Gating & Traceable RAG Grounding  

---

## 1. Visual Evidence Inventory

| File Name | Format | Date Captured | Subject / Purpose | Associated Architecture Stage |
| :--- | :---: | :---: | :--- | :--- |
| [**Screenshot from 2026-09-15 12-32-19.png**](file:///d:/Sacco-Agent/evidence/screenshots/Screenshot%20from%202026-09-15%2012-32-19.png) | PNG (26.8 KB) | 2026-09-15 | **Controlled RAG Architecture Flow:** End-to-end knowledge ingestion from approved policy docs to vector DB, query retrieval, context construction, and grounded foundation model response. | Knowledge Preparation & Query-Answering Pipelines |
| [**Screenshot from 2026-09-24 13-37-19.png**](file:///d:/Sacco-Agent/evidence/screenshots/Screenshot%20from%202026-09-24%2013-37-19.png) | PNG (22.6 KB) | 2026-09-24 | **Full System Architecture & Boundary Matrix:** Separation of AI reasoning from deterministic Python tools, persistent memory store, and mandatory human review gate. | System Boundary & Gating Topology |

---

## 2. Walkthrough of Architectural Screenshot Evidence

### 2.1 Controlled RAG Pipeline Architecture (`Screenshot from 2026-09-15 12-32-19.png`)
* **Context:** Documented in [`RAG/Rag.md`](file:///d:/Sacco-Agent/RAG/Rag.md).
* **Key Evidence Demonstrated:**
  1. **Controlled Ingestion:** Ingestion of 20 approved UMRA and SACCO documents with metadata preservation (Source ID, Section headings, Approval dates).
  2. **Chunking & Embeddings:** Dividing large manuals into discrete, cited chunks stored in the vector database.
  3. **Dual Pipeline Execution:** Strict bifurcation between offline Knowledge Preparation and real-time Query Processing.
  4. **Grounding Constraint:** The foundation model operates purely as a synthesizer of retrieved context; if policy evidence is missing, it emits an `Insufficient Evidence` alert rather than hallucinating rules.

### 2.2 System Architecture & Safety Gating (`Screenshot from 2026-09-24 13-37-19.png`)
* **Context:** Documented in [`README.md`](file:///d:/Sacco-Agent/README.md) and [`docs/project-charter.md`](file:///d:/Sacco-Agent/docs/project-charter.md).
* **Key Evidence Demonstrated:**
  1. **UI Layer:** Loan Officer interface for case intake and interactive review.
  2. **Deterministic Service Layer:** Repayment amortization calculator, DSR computation, member record validator, and session memory store.
  3. **Orchestration Firewall:** Sits between the UI/Model and external actions; strictly bars high-impact methods (`approve_loan`, `disburse_funds`).
  4. **Human Review Endpoint:** All draft briefs terminate in `AWAITING_LOAN_OFFICER_REVIEW` for subsequent transmission to the Credit Committee.

---

## 3. UI Prototype Interaction Progressions

The working Streamlit prototype ([`evidence/demo/sacco_baseline/app.py`](file:///d:/Sacco-Agent/evidence/demo/sacco_baseline/app.py)) implements these architectural components visually:
1. **Intake Panel:** Selects synthetic member profiles (`SACCO-M-001` through `SACCO-M-010`) and captures requested facility amounts and terms.
2. **Deterministic Schedule View:** Displays exact reducing-balance installment tables with total principal and interest.
3. **Policy Evidence Inspector:** Shows the exact retrieved markdown chunks from [`/RAG`](file:///d:/Sacco-Agent/RAG) supporting each rule check.
4. **Draft Case Brief:** Presents verified findings, missing item checklists, and formal handoff warnings.
