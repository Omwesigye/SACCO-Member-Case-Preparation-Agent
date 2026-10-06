"""
Synthetic data store for the SACCO bounded agent workflow demo.
Mirrors the member record shape already used elsewhere in the project
(member_001.json etc.) and a small policy snippet set keyed by topic,
standing in for the real RAG policy corpus.
"""

MEMBERS = {
    "SACCO-M-001": {
        "member_id": "SACCO-M-001",
        "full_name": "Synthetic Member One",
        "membership_months": 30,
        "monthly_income": 1500000,
        "monthly_savings": 300000,
        "savings_balance": 4500000,
        "existing_monthly_obligations": 250000,
        "requested_loan": 6000000,
        "requested_term_months": 12,
        "annual_interest_rate": 18,
        "kyc_status": "verified",
        "has_arrears": False,
        "number_of_guarantors": 2,
        "data_type": "synthetic",
    },
    "SACCO-M-002": {
        "member_id": "SACCO-M-002",
        "full_name": "Synthetic Member Two",
        "membership_months": 18,
        "monthly_income": 1200000,
        "monthly_savings": 200000,
        "savings_balance": 2800000,
        "existing_monthly_obligations": 150000,
        "requested_loan": 4000000,
        "requested_term_months": 12,
        "annual_interest_rate": 18,
        "kyc_status": "missing",          # deliberately incomplete
        "has_arrears": False,
        "number_of_guarantors": 2,
        "data_type": "synthetic",
    },
    # Note: SACCO-M-999 is intentionally NOT in this dict.
    # Looking it up is used to trigger the "member not found" stop condition.
}

# Minimal stand-in for the real 20-document RAG corpus: a handful of
# topic-tagged policy snippets with the same citation fields the real
# pipeline uses (Source ID / Doc / Section), so retrieval behaves the
# same way structurally.
POLICY_SNIPPETS = [
    {
        "topic": "eligibility",
        "source_id": "SACCO-CREDIT-001",
        "doc": "Credit Policy and Lending Procedures Manual (v3.0)",
        "section": "3. General Borrower Eligibility Criteria",
        "text": "Must have been an active, registered member for a minimum of "
                "six (6) consecutive calendar months prior to the date of application.",
    },
    {
        "topic": "dsr",
        "source_id": "SACCO-CREDIT-001",
        "doc": "Credit Policy and Lending Procedures Manual (v3.0)",
        "section": "5. Repayment Capacity and Debt Service Ratio (DSR)",
        "text": "Total monthly debt obligations must not exceed 50% of the "
                "applicant's verifiable net monthly income.",
    },
    {
        "topic": "kyc",
        "source_id": "SACCO-AML-001",
        "doc": "Anti-Money Laundering, CFT & KYC Compliance Policy (v3.0)",
        "section": "2. Customer Due Diligence (CDD) and KYC Tiers",
        "text": "Full legal name verified against National ID (NIN); physical "
                "address corroborated by LC1 Chairperson letter.",
    },
    {
        "topic": "guarantor",
        "source_id": "SACCO-CREDIT-001",
        "doc": "Credit Policy and Lending Procedures Manual (v3.0)",
        "section": "6. Security and Guarantor Requirements",
        "text": "Every loan facility must be secured to a minimum of 100% of "
                "the loan principal plus anticipated interest.",
    },
]
