---
source_id: "SACCO-FIN-001"
title: "Accounting and Financial Procedures Manual"
document_type: "Internal Procedures Manual"
owner: "SACCO Board / Finance & Accounts Department"
issuing_authority: "SACCO Board of Directors"
version: "v2.1"
approval_date: "2026-01-22"
effective_date: "2026-02-01"
origin: "SACCO internal document"
file_name: "06_accounting_and_financial_procedures_manual.md"
official_publication_link: "ref://sacco/fin/afm-2026"
access_status: "Approved for RAG prototype"
confidentiality: "Internal"
review_status: "Verified by Chief Accountant"
hash_or_checksum: "sha256:4b227777d4dd934ecff4f6b55447a16b9b1d9bf5b37e96b797f261ec0de71650"
relevant_sections: "Section 3 (Disbursement Procedures & Net Payout), Section 4 (Interest & Fee Accounting), Section 5 (Repayment Appropriation Order), Section 6 (Write-off Protocols)"
relevance: "Specifies financial accounting treatment for loan disbursement deductions, net funds paid, repayment waterfalls, and interest suspension."
---

# Accounting and Financial Procedures Manual

## 1. Accounting Standards and Legal Framework
* **1.1 Accounting Basis:** The SACCO prepares its financial accounts on an accrual basis in accordance with International Financial Reporting Standards (IFRS for SMEs) and reporting guidelines specified by UMRA under the Tier 4 Microfinance Institutions and Money Lenders Act, 2016.
* **1.2 Dual Authorization Principle:** All financial vouchers, loan disbursements, ledger adjustments, and bank transfers require dual signatory approval (Originator + Authorizer).

## 2. General Ledger Chart of Accounts for Credit Operations
The SACCO maintains dedicated asset, liability, and revenue accounts for credit operations:
* `11200` — Member Loans Outstanding (Gross Asset)
* `11290` — Allowance for Loan Impairment / Credit Losses (Contra-Asset)
* `21100` — Compulsory Member Savings (Liability)
* `21200` — Voluntary Member Savings (Liability)
* `41100` — Interest Income on Member Loans (Revenue)
* `41200` — Loan Processing and Appraisal Fees (Revenue)
* `41300` — Insurance Levy Reserve (Escrow / Liability)

## 3. Loan Disbursement Accounting and Net Payout Calculation
* **3.1 Deduction of Upfront Charges:**
  At the moment of disbursement, the approved upfront fees (appraisal fee, insurance levy, registration charges) are deducted from the approved gross loan amount.
  $$\text{Net Disbursed Amount} = \text{Gross Approved Loan} - (\text{Appraisal Fee} + \text{Insurance Levy} + \text{Loan Agreement Fee})$$
* **3.2 Permissible Disbursement Channels:**
  * Direct Electronic Funds Transfer (EFT) to the member’s verified commercial bank account.
  * Mobile Money transfer to the member's registered SIM card (registered under member’s verified National ID).
  * Account transfer directly into the member’s Voluntary Savings account.
  * Under no circumstances shall cash disbursements exceeding UGX 500,000 be made across the counter.

## 4. Interest Income Recognition and Suspension Rules
* **4.1 Performing Facilities:** Interest on active performing loans (Days Past Due $\le 60$ days) is recognized on an accrual basis monthly.
* **4.2 Non-Performing Loans & Interest in Suspense:**
  * Once a loan is classified as **Substandard** (exceeds 60 days past due), interest accrual ceases immediately in the Profit & Loss statement.
  * Any uncollected accrued interest is transferred to the **Interest in Suspense Account** (`11295`) and recognized only when cash payment is physically received.

## 5. Repayment Appropriation Waterfall
When a loan installment is received from a member or realized through guarantor offset, the funds must be appropriated in the following mandatory sequence:
1. **Statutory Recovery Charges & Legal Fees** (if any incurred).
2. **Contractual Penalty Fees** (for late payment).
3. **Accrued Contractual Interest**.
4. **Loan Principal**.
Under no circumstances may interest or principal be prioritized over recovery charges already incurred by the SACCO.

## 6. Bad Debt Write-Off and Post-Write-off Recoveries
* **6.1 Write-Off Authority:** Only loans classified as **Loss** ($>180$ days past due) that have exhausted all recovery avenues (guarantor attachment, asset execution) may be recommended for write-off.
* **6.2 Approval Mechanism:** Write-offs require initial review by the Supervisory Committee, recommendation by the Board of Directors, and formal ratification by the Annual General Meeting (AGM), accompanied by notification to UMRA.
* **6.3 Continued Liability:** Write-off is an internal accounting adjustment and does not extinguish the member's legal obligation to repay.
