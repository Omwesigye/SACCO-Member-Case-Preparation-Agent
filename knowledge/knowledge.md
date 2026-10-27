# Knowledge Corpus & Provenance Index

This directory serves as the metadata and provenance registry for the **SACCO Member Case Preparation Agent** knowledge corpus.

Per the assignment specification:
> *"Ground model behaviour using trusted context and retrieval rather than relying only on model memory."*

---

## 1. Corpus Location & Structure

The complete institutional knowledge corpus is stored in the [RAG/](file:///c:/Users/USER/OneDrive/Desktop/SACCO%20PROJECT/SACCO-Member-Case-Preparation-Agent/RAG/) directory. It consists of **20 approved, provenance-tracked policy documents** structured in Markdown with standardized YAML frontmatter headers:

| Doc # | Source ID | Title | Scope |
|---|---|---|---|
| **01** | `SACCO-BYLAW-001` | SACCO Bylaws & Governance Framework | Membership qualification, member rights, voting, withdrawal |
| **02** | `SACCO-CREDIT-001` | Credit Policy & Lending Procedures Manual | Loan appraisal, exposure limits, DSR thresholds (50%), repayment rules |
| **03** | `SACCO-SAVINGS-001` | Savings & Deposits Policy | Mandatory savings, withdrawal restrictions, collateral lien |
| **04** | `SACCO-PROD-001` | Loan Product Catalogue | Development, School Fees, Emergency, Agri loans (interest & tenors) |
| **05** | `SACCO-RISK-001` | Credit Risk Management Policy | Credit limits, provisioning, arrears classifications |
| **06** | `SACCO-FIN-001` | Accounting & Financial Procedures Manual | Loan amortization, reducing-balance method, interest recognition |
| **07** | `SACCO-GOV-001` | Governance & Committee Terms of Reference | Credit Committee approval limits, supervisory committee powers |
| **08** | `SACCO-AML-001` | AML/CFT & KYC Compliance Policy | Level 1 & Level 2 KYC requirements, PEP screening |
| **09** | `SACCO-COMP-001` | Consumer Protection & Complaints Policy | Transparency, fee disclosures, dispute mechanisms |
| **10** | `SACCO-DATA-001` | Data Protection & Information Security Policy | Member privacy, record retention, access controls |
| **11** | `SACCO-FORM-001` | Loan Application Form & Checklist | Standard application fields and required attachments |
| **12** | `SACCO-CHECK-001` | Loan Appraisal Checklist | Checklist used by loan officers before committee submission |
| **13** | `SACCO-GUAR-001` | Guarantor Agreement & Guarantee Form | Guarantor qualifications, liability, replacement rules |
| **14** | `SACCO-SCHED-001` | Repayment Schedule Template & Calculation Rules | Amortization formulas, reducing-balance definitions |
| **15** | `SACCO-MEMBER-001` | Synthetic Member Record Schema & Data Dictionary | Schema definitions for synthetic member profiles |
| **16** | `SACCO-CASE-001` | Synthetic Sample Case Pack | Complete end-to-end sample case pack for evaluation |
| **17** | `SACCO-REG-001` | Tier 4 Microfinance Institutions Act Guidance | Statutory lending limits, licensing, non-deposit compliance |
| **18** | `SACCO-REG-002` | UMRA Consumer Protection Guidance | Fair treatment, clear disclosure of effective interest rates |
| **19** | `SACCO-REG-003` | Relevant SACCO Credit & Liquidity Regulations | Statutory liquidity ratios, reserve requirements |
| **20** | `SACCO-RATE-001` | Board-Approved Interest Rate & Fee Schedule | Official active APRs, processing fees, loan insurance fees |

---

## 2. Provenance & Metadata Register

For full document provenance, effective dates, approval authorities, chunking breakdown (121 section-level chunks), and citation mapping, refer to:
- **[RAG/source_register.md](file:///c:/Users/USER/OneDrive/Desktop/SACCO%20PROJECT/SACCO-Member-Case-Preparation-Agent/RAG/source_register.md)**

---

## 3. Data Confidentiality & Integrity Rules

- **Zero Confidential Institutional Data:** No confidential or real member data is committed to this repository. All member records are strictly synthetic.
- **Deterministic Administrative Changes:** Policies can only be added, updated, or archived via administrative workflows; the AI agent has read-only retrieval permissions.
