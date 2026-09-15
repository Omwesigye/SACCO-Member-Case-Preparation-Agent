# 10-Case Prompt Evaluation Table

**Capability under test:** AI Case Preparation + Output Validation 
**Model used:** OpenAI GPT-5 (via OpenAI API)
**Prompt version tested:** v1.0
**Dataset:** 10 synthetic member profiles, each testing a distinct rule or edge case (real outputs from the application)

| # | Test Input | Expected Behaviour | Actual Behaviour | Pass/Fail |
|---|---|---|---|---|
| 1 | member_001 (6,000,000 UGX, 12mo, verified KYC, no arrears, 2 guarantors) | All rules pass except guarantor (pending) | All rules PASS except guarantor (PENDING_EVIDENCE); repayment correctly labeled illustrative | Pass (validator false-positive on negated "recommend approval/rejection" phrase) |
| 2 | member_002 (4,000,000 UGX, 12mo, missing KYC, no arrears) | Missing KYC correctly flagged as pending, not assumed | KYC correctly flagged PENDING_EVIDENCE; all other applicable rules PASS | Pass (validator false-positive on "recommend approving") |
| 3 | member_003 (8,000,000 UGX, 36-month term — exceeds 24mo max) | Term-length rule should FAIL, not be silently ignored or auto-adjusted | Repayment Term correctly flagged FAIL; explained the 36 vs 24-month conflict; full brief still completed for human review | Pass |
| 4 | member_004 (has_arrears = true, all other fields normal) | Arrears rule should trigger additional-review requirement | Arrears check returned a new, more severe status: EXCEPTION_REQUIRED (not just FAIL/PENDING); correctly explained and listed as a required human review item | Pass — new status category (EXCEPTION_REQUIRED) identified |
| 5 | member_005 (2 months membership — below 6mo minimum) | Membership rule should FAIL | Membership check correctly returned FAIL, explaining 2 vs 6-month minimum; other rules evaluated normally around it | Pass |
| 6 | member_006 (3-month term — below 6mo minimum) | Term rule should FAIL from the low side, not just the high side | Repayment Term correctly returned FAIL, citing the 6–24 month range violated from below | Pass — confirms term check works in both directions |
| 7 | member_007 (income 700,000 vs obligations 500,000 — high debt load, all formal rules pass) | All rules PASS, but AI should still flag affordability concern for human review | All rules PASS; AI proactively flagged disposable income (200,000) vs illustrative payment (458,399.96) as a debt-servicing risk | Pass — shows reasoning beyond binary rule-checking |
| 8 | member_008 (missing KYC AND has_arrears = true, simultaneously) | Both issues should be caught, not just the first one found | KYC returned PENDING_EVIDENCE; Arrears returned EXCEPTION_REQUIRED; both correctly listed as required human actions | Pass — confirms multiple simultaneous issues are not dropped |
| 9 | member_009 (0 guarantors declared) | Guarantor rule should reflect that guarantors are actually absent | Flagged PENDING_EVIDENCE — same category used for members with 2–3 guarantors awaiting confirmation | Partial pass — correct outcome, but system doesn't distinguish "0 provided" from "provided but unconfirmed" |
| 10 | member_010 ("ideal" profile: 36mo membership, strong income, no arrears, verified KYC, 3 guarantors) | All rules should PASS cleanly as a control case | All rules PASS (guarantor still correctly PENDING_EVIDENCE, since that's always required regardless of count) | Pass — confirms baseline works correctly with no manufactured failures |

**Overall:** 9/10 cases show the core AI behaviour (policy retrieval, rule-checking, deterministic calculation, human-review boundary) working correctly across a genuinely broad range of scenarios, clean pass, missing KYC, term violations (both above and below range), membership shortfall, arrears, combined failures, high debt-to-income, zero guarantors, and a clean control case.
