import json
from pathlib import Path

import streamlit as st

from calculator import (
    calculate_repayment,
    generate_schedule
)

from policy_loader import load_all_policies

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
        "member_003_invalid_term.json"
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
# POLICY SECTION
# ---------------------------------------------------------

st.header(
    "2. Approved SACCO Policies"
)

policies = load_all_policies()

with st.expander(
    "View policies supplied to the AI"
):

    st.text(policies)


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

    case_prompt = build_case_prompt(
        member=member,
        policies=policies,
        repayment=repayment
    )

    try:

        with st.spinner(
            "Preparing case..."
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
        # SHOW RESULT
        # -------------------------------------------------

        st.header(
            "5. Draft Case Brief"
        )

        st.markdown(
            ai_response
        )


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
