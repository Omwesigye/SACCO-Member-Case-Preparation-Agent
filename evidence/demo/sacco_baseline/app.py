import json
from pathlib import Path

import streamlit as st

from calculator import (
    calculate_repayment,
    generate_schedule
)

from policy_loader import (
    load_all_policies,
    get_rag_pipeline,
    retrieve_case_evidence,
    retrieve_query_evidence
)

from prompts import build_case_prompt

from llm_service import prepare_case_with_ai

from validator import validate_ai_response



st.set_page_config(
    page_title="SACCO Case Preparation Assistant",
    page_icon="🏦",
    layout="wide"
)



DATA_FOLDER = Path(__file__).parent / "data"


def load_member(filename):

    path = DATA_FOLDER / filename

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def format_money(value):

    return f"UGX {value:,.2f}"


# ---------------------------------------------------------
# PAGE HEADER
# ---------------------------------------------------------

st.title(
    "🏦 SACCO Case Preparation Assistant"
)

st.caption(
    "Working Baseline Model Interaction"
)

st.warning(
    """
    This prototype uses synthetic member data.

    It prepares cases for human review only.

    It does NOT approve loans, decline loans,
    disburse funds, or modify SACCO accounts.
    """
)


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.header(
    "Test Cases"
)

member_file = st.sidebar.selectbox(
    "Select a synthetic member",
    [
        "member_001.json",
        "member_002_missing_kyc.json",
        "member_003_invalid_term.json",
        "member_004_arrears.json",
        "member_005_new_member.json",
        "member_006_short_term.json",
        "member_007_high_debt.json",
        "member_008_unverified_kyc_arrears.json",
        "member_009_zero_guarantors.json",
        "member_010_perfect_profile.json"
    ]
)


# ---------------------------------------------------------
# LOAD MEMBER
# ---------------------------------------------------------

try:

    member = load_member(
        member_file
    )

except Exception as error:

    st.error(
        f"Could not load member: {error}"
    )

    st.stop()


# ---------------------------------------------------------
# MEMBER INFORMATION
# ---------------------------------------------------------

st.header(
    "1. Application Intake"
)

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Member ID",
        member["member_id"]
    )

    st.metric(
        "Membership",
        f'{member["membership_months"]} months'
    )


with col2:

    st.metric(
        "Requested Loan",
        format_money(
            member["requested_loan"]
        )
    )

    st.metric(
        "Requested Term",
        f'{member["requested_term_months"]} months'
    )


with col3:

    st.metric(
        "KYC Status",
        member["kyc_status"].upper()
    )

    st.metric(
        "Guarantors",
        member["number_of_guarantors"]
    )


with st.expander(
    "View full synthetic member record"
):

    st.json(member)


# ---------------------------------------------------------
# POLICY SECTION (GROUNDED RAG RETRIEVAL)
# ---------------------------------------------------------

st.header(
    "2. Grounded SACCO Policy Retrieval (RAG)"
)

rag_pipeline = get_rag_pipeline()
st.caption(
    f"Connected to Controlled Knowledge Corpus ({len(rag_pipeline.retriever.chunks)} policy chunks indexed across 20 approved documents)."
)

# Retrieve case-tailored policy evidence for the selected member
case_evidence = retrieve_case_evidence(member=member, repayment={}, max_chunks=4)

tab1, tab2 = st.tabs(["Case-Tailored Policy Evidence", "Interactive Policy Query"])

with tab1:
    st.write(f"Relevant policy evidence retrieved for **Member {member['member_id']}**:")
    for ev in case_evidence:
        c = ev.chunk
        with st.expander(f"📌 [{ev.relevance_tier}] {c.source_id} — {c.document_title} | {c.section_heading} (Score: {ev.score:.3f})"):
            st.markdown(f"**Document:** {c.document_title} ({c.version}) | **Effective:** {c.effective_date}")
            st.markdown(f"**Section:** {c.section_heading}")
            st.markdown(f"**Citation:** `{ev.citation}`")
            st.text(c.content)

with tab2:
    st.subheader("Query SACCO Policy Knowledge Base")
    user_query = st.text_input(
        "Enter a policy question:",
        placeholder="e.g. What are the requirements for Level 2 KYC or guarantor limits?"
    )
    if user_query:
        query_results = retrieve_query_evidence(user_query, top_k=3)
        if query_results:
            for qev in query_results:
                qc = qev.chunk
                st.markdown(f"**{qc.source_id} — {qc.document_title}** | *{qc.section_heading}* (Relevance: `{qev.relevance_tier}`, Score: `{qev.score:.3f}`)")
                st.info(f"**Citation:** `{qev.citation}`\n\n{qc.content[:350]}...")
        else:
            st.warning("No matching policy evidence found above threshold. Response will state 'Insufficient Evidence'.")


# ---------------------------------------------------------
# DETERMINISTIC CALCULATION
# ---------------------------------------------------------

st.header(
    "3. Deterministic Repayment Calculator"
)

try:

    repayment = calculate_repayment(
        principal=member[
            "requested_loan"
        ],
        annual_rate=member[
            "annual_interest_rate"
        ],
        months=member[
            "requested_term_months"
        ]
    )

    schedule = generate_schedule(
        principal=member[
            "requested_loan"
        ],
        annual_rate=member[
            "annual_interest_rate"
        ],
        months=member[
            "requested_term_months"
        ]
    )

except ValueError as error:

    st.error(str(error))

    st.stop()


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Illustrative Monthly Payment",
        format_money(
            repayment[
                "monthly_payment"
            ]
        )
    )


with col2:

    st.metric(
        "Illustrative Total Interest",
        format_money(
            repayment[
                "total_interest"
            ]
        )
    )


with col3:

    st.metric(
        "Illustrative Total Repayment",
        format_money(
            repayment[
                "total_repayment"
            ]
        )
    )


st.info(
    """
    These figures were calculated by deterministic Python
    software.

    The AI does not calculate or modify these values.

    The schedule is illustrative and is not a loan offer.
    """
)


with st.expander(
    "View full repayment schedule"
):

    st.dataframe(
        schedule,
        use_container_width=True
    )


# ---------------------------------------------------------
# AI CASE PREPARATION
# ---------------------------------------------------------

st.header(
    "4. AI Case Preparation"
)

st.write(
    """
    The AI receives:

    - the synthetic member information
    - the approved SACCO policies
    - the deterministic repayment result

    It then prepares a draft case brief for human review.
    """
)


if st.button(
    "Prepare Case for Human Review",
    type="primary"
):

    case_prompt = rag_pipeline.build_case_prompt(
        member=member,
        repayment=repayment,
        evidence=case_evidence
    )

    try:

        with st.spinner(
            "Preparing case using retrieved policy evidence..."
        ):

            ai_response = prepare_case_with_ai(
                case_prompt
            )


        # -------------------------------------------------
        # VALIDATE AI RESPONSE
        # -------------------------------------------------

        problems = validate_ai_response(
            ai_response
        )


        # -------------------------------------------------
        # SHOW RESULT & SOURCE CITATIONS
        # -------------------------------------------------

        st.header(
            "5. Draft Case Brief"
        )

        st.markdown(
            ai_response
        )

        st.subheader("📚 Supporting Document & Source References")
        evidence_data = []
        for ev in case_evidence:
            evidence_data.append({
                "Source ID": ev.chunk.source_id,
                "Document Title": ev.chunk.document_title,
                "Version": ev.chunk.version,
                "Section": ev.chunk.section_heading,
                "Relevance": ev.relevance_tier,
                "Match Score": f"{ev.score:.3f}"
            })
        st.table(evidence_data)


        # -------------------------------------------------
        # SAFETY VALIDATION
        # -------------------------------------------------

        st.header(
            "6. Output Validation"
        )


        if problems:

            st.error(
                """
                The validator detected a possible
                decision-boundary violation.
                """
            )

            for problem in problems:

                st.write(
                    f"- {problem}"
                )

        else:

            st.success(
                """
                Baseline validation passed.

                No obvious automated approval,
                rejection or disbursement statement
                was detected.
                """
            )


        # -------------------------------------------------
        # HUMAN CONTROL
        # -------------------------------------------------

        st.header(
            "7. Human Review"
        )

        st.warning(
            """
            WORKFLOW ENDS HERE.

            An authorized SACCO officer must review
            the case.

            The AI cannot approve or decline the loan.
            """
        )


    except Exception as error:

        st.error(
            f"""
            The AI request failed.

            Error:

            {error}
            """
        )
