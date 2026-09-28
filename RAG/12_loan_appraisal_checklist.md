---
source_id: "SACCO-FORM-002"
title: "Loan Appraisal, Verification and Due Diligence Checklist"
document_type: "Operational Due Diligence Checklist"
owner: "Credit Department / Credit Committee"
issuing_authority: "Head of Credit / SACCO Board"
version: "v2.2"
approval_date: "2026-01-18"
effective_date: "2026-02-01"
origin: "SACCO internal tool"
file_name: "12_loan_appraisal_checklist.md"
official_publication_link: "ref://sacco/forms/chk-2026"
access_status: "Approved for RAG prototype"
confidentiality: "Internal / Credit Officers"
review_status: "Verified by Credit Committee"
hash_or_checksum: "sha256:3a772c5123bbdae3a479ff7380126da39611f7cae8bba104278ec0cb4901f4c3"
relevant_sections: "Section 1 (Core Eligibility Gate), Section 2 (Capacity & DSR Check), Section 3 (Collateral & Guarantors Audit), Section 4 (KYC & Compliance), Section 5 (Summary Result & Recommendation)"
relevance: "Defines the exact 13-point verification rules and status outcomes (Pass / Fail / Exception) evaluated during automated and manual case appraisal."
---

# Loan Appraisal, Verification and Due Diligence Checklist

**Case ID:** `CASE-2026-__________` | **Member ID:** `M-__________` | **Loan Product:** `____________________`  
**Loan Officer:** `____________________` | **Branch:** `____________________` | **Date of Appraisal:** `[DD/MM/YYYY]`

---

## 1. Core Membership & Policy Eligibility Gate
| # | Appraisal Check Item | Policy Standard Ref. | Verified System Data | Result (Pass / Fail / Exception) | Officer Notes / Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1.1 | **Membership Duration** | $\ge 6$ consecutive months (`SACCO-CREDIT-001 §3.1`) | `____ Months` | `[ ] Pass  [ ] Fail` | Member joined date: `DD/MM/YYYY` |
| 1.2 | **Paid-Up Share Capital** | Minimum 20 shares (UGX 200,000) (`SACCO-BYLAW-001 §3.3`) | `UGX ____________` (`____ Shares`) | `[ ] Pass  [ ] Fail` | Share ledger verified. |
| 1.3 | **Savings Consistency** | Minimum 6 months regular deposits (`SACCO-CREDIT-001 §3.3`) | `____ Consecutive Months` | `[ ] Pass  [ ] Fail` | No broken savings months. |
| 1.4 | **Delinquency Status** | Zero active arrears; no default in last 12m (`SACCO-CREDIT-001 §3.4`) | Current PAR: `__ Days` | `[ ] Pass  [ ] Fail` | Core banking loan ledger checked. |
| 1.5 | **Savings Multiplier** | Max 3x (Commercial) or 4x (Agri) (`SACCO-CREDIT-001 §4.1`) | Free Savings: `UGX ________` Ratio: `____x` | `[ ] Pass  [ ] Fail` | Loan requested vs unencumbered savings. |
| 1.6 | **Single Borrower Exposure** | $\le 5\%$ of SACCO Core Capital (`UMRA-SACCO-REG-003 Reg 12`) | Total SACCO Exposure: `UGX ________` | `[ ] Pass  [ ] Fail` | Below institutional statutory cap. |

---

## 2. Capacity & Affordability Evaluation (DSR Check)
* **2.1 Net Verifiable Monthly Income:** `UGX ____________________` (Derived from 3m pay slips / 6m cash books)
* **2.2 Proposed Monthly Loan Installment:** `UGX ____________________` (Derived from reducing-balance schedule)
* **2.3 Other Existing Monthly Debt Repayments:** `UGX ____________________`
* **2.4 Total Debt Commitments (Proposed + Existing):** `UGX ____________________`
* **2.5 Debt Service Ratio (DSR) Calculation:**
  $$\text{DSR} = \frac{\text{Total Debt Commitments}}{\text{Net Monthly Income}} \times 100\% = \frac{\text{UGX ____________}}{\text{UGX ____________}} \times 100\% = \mathbf{\_\_\_\_\_\%}$$
* **Affordability Result:**  
  `[ ] Pass (DSR <= 50.0%)`  
  `[ ] Fail (DSR > 50.0% - Affordability threshold breached)`  
  `[ ] Exception Required (DSR 50.1% - 55.0% backed by secondary verifiable guarantor cash)`

---

## 3. Collateral & Guarantor Audit
| Check Item | Standard Required | Verified Finding | Status |
| :--- | :--- | :--- | :--- |
| **Total Security Coverage** | $\ge 100\%$ of Principal + Interest (`SACCO-CREDIT-001 §6.1`) | Total Collateral: `UGX ____________` | `[ ] Pass  [ ] Fail` |
| **Guarantor 1 Eligibility** | Active $\ge 6$m, free savings $\ge$ pledged sum (`SACCO-CREDIT-001 §6.3`) | Free Savings: `UGX ____________` Pledged: `UGX ____________` | `[ ] Pass  [ ] Fail` |
| **Guarantor 2 Eligibility** | Active $\ge 6$m, free savings $\ge$ pledged sum (`SACCO-CREDIT-001 §6.3`) | Free Savings: `UGX ____________` Pledged: `UGX ____________` | `[ ] Pass  [ ] Fail` |
| **Physical Collateral / Asset** | Valuation report valid; on-site visit conducted; SIMPO checked | Asset: `________________________` Valuation: `UGX ____________` | `[ ] Pass  [ ] N/A` |

---

## 4. KYC, Due Diligence & Compliance Screening
* **Level 2 KYC Dossier:** Valid National ID (NIN) verified, LC1 verification attached, physical address visited (`SACCO-AML-001 §2.2`). `[ ] Complete  [ ] Deficient`
* **Politically Exposed Person (PEP) Status:** `[ ] Non-PEP   [ ] PEP (Escalation to Board required)`
* **Credit Reference Bureau (CRB) Status:** Inquired on: `[DD/MM/YYYY]` | Score: `____` | Negative listings: `[ ] None   [ ] Present`

---

## 5. Overall Appraisal Verdict & Routing
* **Overall Outcome:**  
  `[ ] APPROVED FOR ROUTING (Meets 100% of policy parameters without deviation)`  
  `[ ] PENDING EVIDENCE (Documentation missing; returned to Applicant)`  
  `[ ] REJECTED (Fails core eligibility/affordability gates)`  
  `[ ] EXCEPTION REQUIRED (Requires Credit Committee / Board discretionary waiver)`
* **Designated Approval Authority Tier:**  
  `[ ] Branch Manager (UGX <= 3M)`  
  `[ ] Credit Committee (UGX 3,000,001 - 20,000,000)`  
  `[ ] Full Board of Directors (> UGX 20M / Insider / Exception)`

* **Appraising Officer Signature:** `____________________________` **Date:** `[DD/MM/YYYY]`  
* **Credit Manager Endorsement:** `____________________________` **Date:** `[DD/MM/YYYY]`
