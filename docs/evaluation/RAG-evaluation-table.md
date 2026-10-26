# 15-Case RAG Evaluation Table

**Capability under test:** Retrieval-Augmented Generation (RAG) — Interactive Policy Query
**Model used:** OpenAI GPT-5 (via OpenAI API)
**Corpus:** 20 approved SACCO policy documents, 121 indexed chunks

| # | Question | Type | Retrieved Sources (real) | Grounding Quality | Pass/Fail |
|---|---|---|---|---|---|
| 1 | Minimum membership duration required before applying for a loan | Answerable | SACCO-CREDIT-001 §3, SACCO-FORM-002 §1 | Correct section retrieved, correctly grounded | Pass |
| 2 | Debt Service Ratio threshold used to assess affordability | Answerable | SACCO-CREDIT-001 §5 (50% rule), SACCO-FORM-002 §2 | Correct section, correct figure retrievable | Pass |
| 3 | Documents required for Level 2 KYC verification | Answerable | SACCO-FORM-002 §4, SACCO-AML-001 §2 (NIN, LC1, address) | Correct, matches exact requirement | Pass |
| 4 | How is the maximum loan amount determined based on a member's savings | Answerable | SACCO-CREDIT-001 §4.1 (3x commercial, 4x agricultural multiplier), SACCO-CREDIT-001 §4.2 (5% core capital limit) | Correct policy section retrieved, savings multiplier and exposure limit verified | Pass |
| 5 | What security/guarantor coverage is required for a loan | Answerable | SACCO-CREDIT-001 §6 (100% coverage), SACCO-SYN-002 §3 | Correct, strong match | Pass |
| 6 | What happens if a member's DSR is exactly at the 50% threshold | Partially answerable | Re-retrieved SACCO-CREDIT-001 §5 — no explicit boundary clarification found | Correctly surfaces the rule; ambiguity is itself the honest finding | Pass |
| 7 | Can a member use pledged savings from a guarantor's account, or only free savings | Partially answerable | SACCO-SAVINGS-001 §4 (Pledged vs Free Savings) | Correct, directly on-topic | Pass |
| 8 | Is there a savings multiplier exception for long-standing members | Partially answerable | Weak match only (SACCO-FORM-002 §1, LOW relevance) | Appropriately weak — no exception exists in policy, system did not invent one | Pass |
| 9 | What happens if a loan applicant has arrears -- can the application proceed | Partially answerable | SACCO-CREDIT-001 §3.4 (Zero active arrears required), SACCO-RISK-001 §4.1 (Automatic delinquency gating & freeze) | Correct, surfaces mandatory arrears gating and escalation to exception review | Pass |
| 10 | Can a member with unverified KYC still receive an illustrative repayment schedule | Partially answerable | SACCO-CREDIT-001 §9 (Loan Case Preparation), SACCO-TMPL-001 §4 (Illustrative schedule disclaimer), SACCO-AML-001 §2.2 | Correctly distinguishes illustrative counseling from formal application gating | Pass |
| 11 | Does the SACCO offer joint or family group loan accounts | Unanswerable | "No matching policy evidence found above threshold. Response will state 'Insufficient Evidence'" | Correct — system properly recognized no coverage | Pass |
| 12 | Does the SACCO support cryptocurrency or mobile-money loan repayments | Unanswerable | Weak match only (SACCO-FORM-001 form fields, LOW relevance) | Grounding failure — should have returned insufficient evidence, instead surfaced irrelevant form fields | Fail |
| 13 | Who is the current chairperson of the Credit Committee | Unanswerable | Weak match only (SACCO-FORM-001 Applicant ID section, LOW relevance) | Grounding failure — same pattern as above | Fail |
| 14 | Can a member transfer their loan balance to another SACCO branch | Unanswerable | Weak match (SACCO-BYLAW-001 §4 Cessation/Withdrawal, LOW relevance) | Grounding failure — retrieved a near-miss (withdrawal, not transfer) instead of flagging insufficient evidence | Fail |
| 15 | Is there a discount or rebate for repaying a loan early, before the full term | Unanswerable | Weak match (SACCO-CREDIT-001 §7 Interest Rate Structure, LOW relevance) — confirmed via live UI test | Grounding failure — exactly the "early vs late penalty" confusion this question was designed to catch | Fail |

## Key Finding

**4 genuine grounding failures identified** (Cases 12, 13, 14, 15), exceeding the assignment's requirement to document at least three retrieval/grounding failures. The pattern is consistent: when a question falls genuinely outside the policy corpus, the system sometimes correctly returns "Insufficient Evidence" (Case 11) but other times retrieves weak, irrelevant matches instead of admitting the gap (Cases 12–15). This inconsistency is a real, evidenced weakness in the retrieval threshold logic, recommended for tuning in a later sprint.

**All 15 cases resolved and verified**: 11 Pass (including 1 clean unanswerable rejection, 5 answerable passes, and 5 partially answerable passes), 4 Fail (grounding failures on out-of-scope questions 12-15 where weak near-miss chunks were surfaced instead of insufficient-evidence flags).
