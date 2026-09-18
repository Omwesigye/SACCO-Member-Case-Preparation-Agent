---
source_id: "SACCO-SYN-002"
title: "Synthetic Member Loan Case Pack — John Okello (Development Loan)"
document_type: "Verification Test Case Pack"
owner: "AI Engineering & Credit Operations"
issuing_authority: "Lead Credit Domain Expert"
version: "v1.0"
approval_date: "2026-02-05"
effective_date: "2026-02-05"
origin: "Project Testing Asset"
file_name: "16_synthetic_sample_case_pack.md"
official_publication_link: "ref://sacco/synth/case-pack-okello-001"
access_status: "Approved for RAG prototype"
confidentiality: "Internal / Synthetic Test Data"
review_status: "Verified by Lead Credit Officer"
hash_or_checksum: "sha256:7c442d8892ca01fe3400a421b8f15e8392cb3356e911da2b4e87009ef32a188c"
relevant_sections: "Section 1 (Case Overview), Section 2 (Policy Evaluation Matrix), Section 3 (Deterministic Amortization Schedule), Section 4 (Risks & Mitigants), Section 5 (Audit Trail & Committee Routing)"
relevance: "Reference standard demonstrating the exact prepared case brief assembled by the agent for Credit Committee review."
---

# Synthetic Member Loan Case Pack

**Case ID:** `CASE-2026-0819`  
**Application Timestamp:** `2026-02-05 09:14 EAT`  
**Assigned Loan Officer:** Grace Tumusiime (ID: `LO-082`)  
**Workflow Status:** `STAFF-REVIEWED — READY FOR CREDIT COMMITTEE`  
**Automated Action Warning:** *This case pack has been assembled by the SACCO Member-Case Preparation Agent. In accordance with SACCO Bylaws and UMRA Regulations, this document is a prepared case brief for human review. It does NOT constitute a loan approval, credit commitment, or disbursement authorization.*

---

## 1. Case Profile & Intake Verification

| Parameter | Declared by Applicant | Verified System Record (`M-04921`) | Status / Variance |
| :--- | :--- | :--- | :--- |
| **Member Full Name** | John Okello | John Okello | Verified Match |
| **NIN** | `CM84021984KL34` | `CM84021984KL34` (NIRA Verified) | Verified Match |
| **Membership Duration** | 24 Months | 23.8 Months (Joined `2024-03-10`) | Verified Match ($\ge 6\text{m}$) |
| **Paid-Up Share Capital**| UGX 300,000 (30 Shares) | UGX 300,000 (30 Shares) | Verified Match ($\ge 20\text{ shares}$) |
| **Current Free Savings** | UGX 4,000,000 | UGX 4,000,000 (Compulsory: 3.6M + Vol: 0.4M) | Verified Match |
| **Loan Product Requested**| Development Loan (`PR-001`)| Development Loan (`PR-001`) | Valid Product Code |
| **Loan Amount Requested** | UGX 10,000,000 | Max Allowed: UGX 12,000,000 (3x Free Savings) | Eligible ($2.5\text{x}$) |
| **Requested Tenor** | 12 Months | Maximum Permitted: 24 Months | Compliant |
| **Monthly Net Income** | UGX 2,500,000 | UGX 2,400,000 (Verified via 6m Bank/Receipts) | Discrepancy reconciled to 2.4M |

---

## 2. Policy Eligibility Matrix & Gating Rules

| Rule ID | Policy Standard Ref. | Rule Description | System Finding | Verdict | Citation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `R-MEM-01` | `SACCO-BYLAW-001 §3.4` | Membership probation $\ge 6$ months | 23.8 months active | **PASS** | [01_sacco_bylaws.md#34](file:///d:/Sacco-Agent/RAG/01_sacco_bylaws.md) |
| `R-SHR-02` | `SACCO-BYLAW-001 §3.3` | Minimum 20 shares (UGX 200,000) | 30 shares (UGX 300,000) | **PASS** | [01_sacco_bylaws.md#33](file:///d:/Sacco-Agent/RAG/01_sacco_bylaws.md) |
| `R-DEL-03` | `SACCO-CREDIT-001 §3.4` | Zero active arrears; 12m clean history | PAR 0 days; 2 past loans paid on time | **PASS** | [02_credit_policy.md#34](file:///d:/Sacco-Agent/RAG/02_credit_policy_and_lending_procedures_manual.md) |
| `R-SAV-04` | `SACCO-CREDIT-001 §4.1` | Max 3.0x multiplier on free savings | UGX 10M / UGX 4M = 2.50x | **PASS** | [02_credit_policy.md#41](file:///d:/Sacco-Agent/RAG/02_credit_policy_and_lending_procedures_manual.md) |
| `R-EXP-05` | `UMRA-SACCO-REG-003 R12` | Single borrower $\le 5\%$ Core Capital | Loan is 1.4% of SACCO Core Capital | **PASS** | [19_sacco_regs.md#r12](file:///d:/Sacco-Agent/RAG/19_relevant_sacco_regulations_credit_liquidity.md) |
| `R-DSR-06` | `SACCO-CREDIT-001 §5.1` | Debt Service Ratio $\le 50.0\%$ | DSR = $38.2\%$ (UGX 916,800 / 2,400,000) | **PASS** | [02_credit_policy.md#51](file:///d:/Sacco-Agent/RAG/02_credit_policy_and_lending_procedures_manual.md) |
| `R-KYC-07` | `SACCO-AML-001 §2.2` | Level-2 KYC Complete (NIN, LC1) | Verified NIN & LC1 on file | **PASS** | [08_aml_kyc.md#22](file:///d:/Sacco-Agent/RAG/08_aml_cft_and_kyc_policy.md) |
| `R-PEP-08` | `SACCO-AML-001 §3.1` | Politically Exposed Person screening | Applicant is not a PEP | **PASS** | [08_aml_kyc.md#31](file:///d:/Sacco-Agent/RAG/08_aml_cft_and_kyc_policy.md) |
| `R-SEC-09` | `SACCO-CREDIT-001 §6.1` | 100% Security Coverage Ratio | 105% Coverage (Savings + 2 Guarantors) | **PASS** | [02_credit_policy.md#61](file:///d:/Sacco-Agent/RAG/02_credit_policy_and_lending_procedures_manual.md) |

---

## 3. Security & Guarantor Backing Breakdown
* **Applicant Pledged Savings:** UGX 4,000,000 (Lien placed)
* **Guarantor 1 (Mary Mbabazi - `M-02115`):** Pledged UGX 3,500,000 (Free savings: UGX 4,200,000; Verified)
* **Guarantor 2 (Peter Atwine - `M-03884`):** Pledged UGX 3,000,000 (Free savings: UGX 3,800,000; Verified)
* **Total Pledged Security Pool:** **UGX 10,500,000** (Coverage: 105.0% of requested principal)

---

## 4. Illustrative Repayment Schedule (Deterministic Output)
* **Interest Basis:** Reducing Balance Amortization @ 1.50% per month (18.0% p.a.)
* **Upfront Payout Deductions:** Appraisal Fee (2.0% = UGX 200,000) + Insurance Levy (1.0% = UGX 100,000) + Agreement Fee (UGX 20,000). **Net Disbursed Cash:** **UGX 9,680,000**.
* **Equated Monthly Installment (EMI):** **UGX 916,800**

| Month | Due Date | Opening Principal (UGX) | Principal Due (UGX) | Interest Due (UGX) | Total Installment (UGX) | Closing Principal (UGX) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 28 Feb 2026 | 10,000,000 | 766,800 | 150,000 | 916,800 | 9,233,200 |
| 2 | 31 Mar 2026 | 9,233,200 | 778,302 | 138,498 | 916,800 | 8,454,898 |
| 3 | 30 Apr 2026 | 8,454,898 | 789,977 | 126,823 | 916,800 | 7,664,921 |
| 4 | 31 May 2026 | 7,664,921 | 801,826 | 114,974 | 916,800 | 6,863,095 |
| 5 | 30 Jun 2026 | 6,863,095 | 813,854 | 102,946 | 916,800 | 6,049,241 |
| 6 | 31 Jul 2026 | 6,049,241 | 826,061 | 90,739 | 916,800 | 5,223,180 |
| 7 | 31 Aug 2026 | 5,223,180 | 838,452 | 78,348 | 916,800 | 4,384,728 |
| 8 | 30 Sep 2026 | 4,384,728 | 851,029 | 65,771 | 916,800 | 3,533,699 |
| 9 | 31 Oct 2026 | 3,533,699 | 863,795 | 53,005 | 916,800 | 2,669,904 |
| 10 | 30 Nov 2026 | 2,669,904 | 876,751 | 40,049 | 916,800 | 1,793,153 |
| 11 | 31 Dec 2026 | 1,793,153 | 889,903 | 26,897 | 916,800 | 903,250 |
| 12 | 31 Jan 2027 | 903,250 | 903,250 | 13,549 | 916,799 | 0 |
| **TOTAL** | — | — | **10,000,000** | **1,001,550** | **11,001,550** | — |

---

## 5. Risk Assessment & Mitigating Factors
* **Identified Risk 1:** Agricultural trading income may exhibit seasonality during dry months (June-July).  
  * *Mitigant:* Applicant maintains secondary stable cash inflows from a 12-cow dairy herd generating steady daily milk proceeds paid bi-weekly.
* **Identified Risk 2:** Exposure of UGX 10,000,000 requires Credit Committee level approval.  
  * *Mitigant:* Total exposure is within the UGX 3M–20M delegated band (`SACCO-GOV-001 §3.3`); 100% security backing secured in liquid SACCO savings.

---

## 6. Case Pack Audit Trail & Next Routing Action
* `2026-02-05 09:14:02` — Application registered; Case ID assigned.
* `2026-02-05 09:14:28` — Member record `M-04921` retrieved from database.
* `2026-02-05 09:14:45` — Policy checks executed (9 of 9 passed; 0 exceptions).
* `2026-02-05 09:15:02` — Illustrative reducing balance schedule generated via calculation tool.
* `2026-02-05 09:16:10` — Loan Officer Grace Tumusiime reviewed brief and endorsed submission.
* **Delegated Next Action:** **Submitted to Credit Committee for meeting on 2026-02-09.**
