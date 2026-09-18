---
source_id: "SACCO-TMPL-001"
title: "Illustrative Reducing-Balance Repayment Schedule Specification & Template"
document_type: "Operational Calculation Specification"
owner: "Finance & Credit Department"
issuing_authority: "Chief Financial Officer / Head of Credit"
version: "v2.0"
approval_date: "2026-01-15"
effective_date: "2026-02-01"
origin: "SACCO calculation template"
file_name: "14_repayment_schedule_template.md"
official_publication_link: "ref://sacco/tmpl/sched-2026"
access_status: "Approved for RAG prototype"
confidentiality: "Operational / Technical"
review_status: "Verified by Finance & IT Systems Lead"
hash_or_checksum: "sha256:5e664f33b1e779a1ec098bb5d3f112e45778841a1200192e4ab34c382103f7e2"
relevant_sections: "Section 1 (Mathematical Specification), Section 2 (Standard Table Format), Section 3 (Benchmark 12-Month Schedule UGX 10M), Section 4 (Rounding & Non-Hallucination Rules)"
relevance: "Defines the exact deterministic formula, column structure, and illustrative reference benchmarks for repayment schedule generation."
---

# Illustrative Reducing-Balance Repayment Schedule Specification & Template

## 1. Mathematical Specification (Equated Monthly Installment - EMI)
In accordance with UMRA consumer transparency rules and [Credit Policy Section 7](file:///d:/Sacco-Agent/RAG/02_credit_policy_and_lending_procedures_manual.md#7-interest-rate-structure-and-calculation-methodology), the SACCO employs the standard **Equal Amortized Monthly Installment (Reducing Balance)** formula:

$$\text{PMT} = P \times \frac{r(1+r)^n}{(1+r)^n - 1}$$

Where:
* $P$ = Loan Principal approved (in UGX)
* $r$ = Periodic Monthly Interest Rate (Annual nominal rate / 12, expressed as a decimal). E.g., for 18% p.a., $r = 0.015$.
* $n$ = Total number of monthly repayment periods.
* $\text{PMT}$ = Total Equated Monthly Installment.

### Monthly Decomposition:
For each period $t \in [1, n]$:
1. **Monthly Interest Due ($I_t$):**
   $$I_t = \text{Opening Balance}_t \times r$$
2. **Monthly Principal Portion ($P_t$):**
   $$P_t = \text{PMT} - I_t$$
3. **Closing Principal Balance ($B_t$):**
   $$B_t = \text{Opening Balance}_t - P_t$$
   *(Where $\text{Opening Balance}_{t+1} = B_t$)*

---

## 2. Standard Table Column Format
Every illustrative schedule generated for a member case brief must follow this layout:

| Month ($t$) | Due Date | Opening Principal (UGX) | Monthly Principal ($P_t$) | Monthly Interest ($I_t$) | Total Installment ($\text{PMT}$) | Closing Principal ($B_t$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |

---

## 3. Reference Benchmark Schedule (Test Verification Standard)
* **Loan Amount ($P$):** UGX 10,000,000
* **Monthly Interest Rate ($r$):** 1.50% per month (18.0% per annum)
* **Tenor ($n$):** 12 Months
* **Calculated Equated Monthly Installment ($\text{PMT}$):** **UGX 916,800** (rounded to nearest 100 UGX)

| Month | Due Date | Opening Balance (UGX) | Principal (UGX) | Interest (UGX) | Total Due (UGX) | Closing Balance (UGX) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | 28 Feb 2026 | 10,000,000 | 766,800 | 150,000 | 916,800 | 9,233,200 |
| **2** | 31 Mar 2026 | 9,233,200 | 778,302 | 138,498 | 916,800 | 8,454,898 |
| **3** | 30 Apr 2026 | 8,454,898 | 789,977 | 126,823 | 916,800 | 7,664,921 |
| **4** | 31 May 2026 | 7,664,921 | 801,826 | 114,974 | 916,800 | 6,863,095 |
| **5** | 30 Jun 2026 | 6,863,095 | 813,854 | 102,946 | 916,800 | 6,049,241 |
| **6** | 31 Jul 2026 | 6,049,241 | 826,061 | 90,739 | 916,800 | 5,223,180 |
| **7** | 31 Aug 2026 | 5,223,180 | 838,452 | 78,348 | 916,800 | 4,384,728 |
| **8** | 30 Sep 2026 | 4,384,728 | 851,029 | 65,771 | 916,800 | 3,533,699 |
| **9** | 31 Oct 2026 | 3,533,699 | 863,795 | 53,005 | 916,800 | 2,669,904 |
| **10** | 30 Nov 2026 | 2,669,904 | 876,751 | 40,049 | 916,800 | 1,793,153 |
| **11** | 31 Dec 2026 | 1,793,153 | 889,903 | 26,897 | 916,800 | 903,250 |
| **12** | 31 Jan 2027 | 903,250 | 903,250 | 13,549 | 916,799 | 0 |
| **TOTAL** | — | — | **10,000,000** | **1,001,550** | **11,001,550** | — |

---

## 4. Deterministic Calculation and Labeling Rules for Agent
* **Mandatory Watermark / Notice:** Every schedule table produced by the agent or calculator must display the following legal disclaimer:  
  `"NOTICE: This schedule is strictly illustrative for credit preparation and financial counseling. It does not constitute a formal loan approval, binding contract, or loan offer."`
* **Zero Model Arithmetic Rule:** The AI language model is strictly barred from inventing or calculating amortization figures in free text. All numbers must originate from the deterministic schedule calculator tool.
* **Rounding Convention:** Currency numbers are rounded to the nearest integer (UGX). The final installment is adjusted by the fractional rounding residual so that the closing balance reaches exactly UGX 0.
