"""
SACCO Member-Case Preparation Agent — Dedicated Streamlit Cockpit
Connects directly to the core backend agent workflow in src/agent/orchestrator.py,
the persistent memory store in src/agent/case_memory.py, deterministic tools,
and the Grounded RAG Pipeline in src/rag/.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import streamlit as st

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Core Agent Imports
from src.agent.orchestrator import run_case_preparation, MAX_ITERATIONS, APPROVED_TOOLS
from src.agent.case_memory import CaseMemoryStore, MemorySafetyViolation
from src.agent.data import MEMBERS

# Safe RAG Pipeline Import
try:
    from src.rag.pipeline import GroundedRAGPipeline
    RAG_AVAILABLE = True
except Exception as e:
    RAG_AVAILABLE = False
    RAG_ERROR = str(e)


# Page Configuration
st.set_page_config(
    page_title="SACCO Member Case Preparation",
    page_icon="blank_favicon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .main-header { font-size: 2.1rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.2rem; }
    .sub-header { font-size: 1.05rem; color: #4B5563; margin-bottom: 1.2rem; }
    .status-badge-ready { background-color: #D1FAE5; color: #065F46; padding: 6px 14px; border-radius: 9999px; font-weight: 700; font-size: 0.95rem; border: 1px solid #10B981; }
    .status-badge-incomplete { background-color: #FEF3C7; color: #92400E; padding: 6px 14px; border-radius: 9999px; font-weight: 700; font-size: 0.95rem; border: 1px solid #F59E0B; }
    .status-badge-locked { background-color: #FEE2E2; color: #991B1B; padding: 6px 14px; border-radius: 9999px; font-weight: 700; font-size: 0.95rem; border: 1px solid #EF4444; }
    .card-metric { background-color: #F9FAFB; padding: 14px; border-radius: 8px; border: 1px solid #E5E7EB; text-align: center; }
    .disclaimer-box { background-color: #EFF6FF; border-left: 4px solid #3B82F6; padding: 12px; margin-top: 15px; border-radius: 4px; font-size: 0.88rem; color: #1E40AF; }
</style>
""", unsafe_allow_html=True)


# Initialize Session State
if "memory_store" not in st.session_state:
    st.session_state.memory_store = CaseMemoryStore()
if "last_trace" not in st.session_state:
    st.session_state.last_trace = None
if "selected_member_id" not in st.session_state:
    st.session_state.selected_member_id = "SACCO-M-001"
if "rag_pipeline" not in st.session_state and RAG_AVAILABLE:
    try:
        st.session_state.rag_pipeline = GroundedRAGPipeline()
    except Exception:
        st.session_state.rag_pipeline = None


def get_trace_stop_reason(t):
    """Safely extract stopping rationale from AgentTrace steps."""
    if not t or not hasattr(t, "steps"):
        return ""
    for s in reversed(t.steps):
        obs = s.get("observe")
        if isinstance(obs, dict) and "reason" in obs:
            return obs["reason"]
    return getattr(t, "stop_reason", "")


def extract_case_policy_evidence(t):
    """Safely extract all policy evidence snippets referenced in the active case."""
    if not t:
        return []
    # 1. Check audit log
    if hasattr(t, "audit_log") and t.audit_log:
        for entry in t.audit_log.entries:
            if entry.get("tool") == "search_sacco_policy":
                res = entry.get("result", {})
                if isinstance(res, dict) and res.get("evidence"):
                    return res["evidence"]
    # 2. Check steps observe
    for s in t.steps:
        obs = s.get("observe")
        if isinstance(obs, dict) and obs.get("evidence"):
            return obs["evidence"]
    # 3. Fallback to default snippets
    from src.agent.data import POLICY_SNIPPETS
    return POLICY_SNIPPETS


# -----------------------------------------------------------------------------
# SIDEBAR: CASE INTAKE & PARAMETER CONTROLS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### **Case Origination Panel**")
    st.caption("Loan Officer Interface • Bounded Agent Engine")

    # Member Profile Selector
    member_keys = list(MEMBERS.keys())
    profile_options = {
        "SACCO-M-001": "SACCO-M-001: John Okello (Eligible, 12m)",
        "SACCO-M-002": "SACCO-M-002: Mary Mbabazi (Missing KYC)",
        "SACCO-M-003": "SACCO-M-003: Patrick Kato (36m Term Violation)",
        "SACCO-M-004": "SACCO-M-004: Agnes Nakato (Active Arrears)",
        "SACCO-M-005": "SACCO-M-005: Emmanuel O. (2m Tenure Low)",
        "SACCO-M-006": "SACCO-M-006: Sarah K. (3m Short Term)",
        "SACCO-M-007": "SACCO-M-007: Joseph M. (High Debt Ratio)",
        "SACCO-M-008": "SACCO-M-008: Grace A. (Missing KYC & Arrears)",
        "SACCO-M-009": "SACCO-M-009: David T. (Zero Guarantors)",
        "SACCO-M-010": "SACCO-M-010: Beatrice N. (Ideal Control)",
        "CUSTOM": "Custom Synthetic ID (e.g. SACCO-M-999)"
    }

    selected_choice = st.selectbox(
        "Select Synthetic Applicant",
        options=list(profile_options.keys()),
        format_func=lambda x: profile_options.get(x, x),
        index=0
    )

    if selected_choice == "CUSTOM":
        target_member_id = st.text_input("Enter Member ID", value="SACCO-M-999")
    else:
        target_member_id = selected_choice

    st.session_state.selected_member_id = target_member_id

    # Load Existing Record
    member_record = MEMBERS.get(target_member_id, {})

    st.markdown("---")
    st.markdown("#### **Loan Facility Parameters**")

    # Editable Loan Inputs
    default_loan = member_record.get("requested_loan", 6000000)
    default_term = member_record.get("requested_term_months", 12)
    default_rate = member_record.get("annual_interest_rate", 18)
    default_income = member_record.get("monthly_income", 1500000)
    default_obligations = member_record.get("existing_monthly_obligations", 250000)
    default_kyc = member_record.get("kyc_status", "verified")
    default_arrears = member_record.get("has_arrears", False)

    req_loan = st.number_input("Requested Principal (UGX)", min_value=100000, max_value=50000000, value=int(default_loan), step=500000)
    req_term = st.slider("Tenor (Months)", min_value=1, max_value=48, value=int(default_term))
    req_rate = st.number_input("Annual Interest Rate (%)", min_value=5.0, max_value=36.0, value=float(default_rate), step=0.5)

    st.markdown("#### **Financial & KYC Profile**")
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        mon_inc = st.number_input("Net Income (UGX)", min_value=0, value=int(default_income), step=100000)
    with col_in2:
        mon_ob = st.number_input("Obligations (UGX)", min_value=0, value=int(default_obligations), step=50000)

    kyc_choice = st.selectbox("KYC Documentation Status", ["verified", "missing"], index=0 if default_kyc == "verified" else 1)
    arrears_choice = st.checkbox("Active Loan Arrears?", value=bool(default_arrears))

    st.markdown("---")
    st.markdown("#### **Staff Review Information**")
    officer_id = st.text_input("Reviewing Loan Officer ID", value="LO-082")
    officer_notes = st.text_area("Narrative Case Notes (Optional)", placeholder="e.g. Member promised to bring LC1 letter tomorrow at 10 AM...")

    # Update working dictionary if existing
    if target_member_id in MEMBERS:
        MEMBERS[target_member_id]["requested_loan"] = req_loan
        MEMBERS[target_member_id]["requested_term_months"] = req_term
        MEMBERS[target_member_id]["annual_interest_rate"] = req_rate
        MEMBERS[target_member_id]["monthly_income"] = mon_inc
        MEMBERS[target_member_id]["existing_monthly_obligations"] = mon_ob
        MEMBERS[target_member_id]["kyc_status"] = kyc_choice
        MEMBERS[target_member_id]["has_arrears"] = arrears_choice

    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("Run Bounded Agent Workflow", type="primary", use_container_width=True)


# -----------------------------------------------------------------------------
# WORKFLOW EXECUTION TRIGGER
# -----------------------------------------------------------------------------
if run_btn:
    with st.spinner(f"Agent executing bounded workflow for {target_member_id}..."):
        try:
            trace = run_case_preparation(
                member_id=target_member_id,
                officer_comment=officer_notes if officer_notes.strip() else None,
                officer_id=officer_id,
                memory_store=st.session_state.memory_store
            )
            st.session_state.last_trace = trace
        except MemorySafetyViolation as msv:
            st.error(f"MEMORY SAFETY VIOLATION INTERCEPTED: {msv}")
        except Exception as e:
            st.error(f"Execution error: {e}")


# -----------------------------------------------------------------------------
# MAIN CONTENT DASHBOARD
# -----------------------------------------------------------------------------
st.markdown('<div class="main-header">SACCO Member Case Preparation</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Interactive Agentic Control Surface • '
    'Deterministic Calculations • Multi-Session Case Memory • UMRA Regulatory Grounding</div>',
    unsafe_allow_html=True
)

trace = st.session_state.last_trace

# TOP BANNER: WORKFLOW STATE & SAFETY GATING
if trace:
    status = trace.status
    col_stat1, col_stat2, col_stat3 = st.columns([2, 1, 1])

    with col_stat1:
        if status == "READY_FOR_REVIEW":
            st.markdown(
                f'<span class="status-badge-ready">STATE: READY_FOR_REVIEW</span> &nbsp; '
                f'<b>Case:</b> {trace.case_id} &nbsp;|&nbsp; <b>Applicant:</b> {trace.member_id}',
                unsafe_allow_html=True
            )
            st.caption("All policy checklists and calculations evaluated. File handed off to Loan Officer for review.")
        elif status == "STOPPED_INCOMPLETE":
            st.markdown(
                f'<span class="status-badge-incomplete">STATE: STOPPED_INCOMPLETE</span> &nbsp; '
                f'<b>Case:</b> {trace.case_id} &nbsp;|&nbsp; <b>Applicant:</b> {trace.member_id}',
                unsafe_allow_html=True
            )
            st.caption("Required documentation or valid member data absent. Agent halted cleanly without guessing.")
        elif status == "STOPPED_COMMITTEE_DECISION_FINAL":
            st.markdown(
                f'<span class="status-badge-locked">STATE: STOPPED_COMMITTEE_DECISION_FINAL</span> &nbsp; '
                f'<b>Case:</b> {trace.case_id}',
                unsafe_allow_html=True
            )
            st.caption("Human approval decision is final. Safety Invariant 3 locked agent from altering verdict.")
        else:
            st.markdown(f"**State:** `{status}`")

    with col_stat2:
        st.metric("Iterations Used", f"{len(trace.steps)} / {MAX_ITERATIONS}")

    with col_stat3:
        cache_reused = getattr(trace, "cached_calculations_reused", 0)
        tool_calcs = getattr(trace, "tool_calculations_executed", 0)
        st.metric("Calculation Cache Hits", f"{cache_reused} reused", f"{tool_calcs} new calls")

    st.markdown("---")
else:
    st.info("Select an applicant profile and click **'Run Bounded Agent Workflow'** in the sidebar to execute.")


# -----------------------------------------------------------------------------
# TABBED WORKSPACE
# -----------------------------------------------------------------------------
tab_brief, tab_trace, tab_governance, tab_rag, tab_audit = st.tabs([
    "Prepared Case Brief",
    "Agent Cognitive Trace",
    "Human Approval Gate",
    "Policy RAG Explorer",
    "Immutable Audit Log"
])


# -----------------------------------------------------------------------------
# TAB 1: PREPARED CASE BRIEF & ELIGIBILITY
# -----------------------------------------------------------------------------
with tab_brief:
    if not trace:
        st.write("No active case brief. Run the agent workflow from the sidebar.")
    elif trace.status == "STOPPED_COMMITTEE_DECISION_FINAL":
        st.error(get_trace_stop_reason(trace))
    else:
        # Load verified member info from record
        mem = MEMBERS.get(target_member_id, {})
        if not mem:
            st.warning(f"Member '{target_member_id}' was not found in the SACCO database. Case preparation halted.")
        else:
            # Top Profile Metrics
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                st.markdown('<div class="card-metric">', unsafe_allow_html=True)
                st.caption("Membership Tenure")
                st.subheader(f"{mem.get('membership_months', 0)} Mos")
                st.markdown('</div>', unsafe_allow_html=True)
            with col_m2:
                st.markdown('<div class="card-metric">', unsafe_allow_html=True)
                st.caption("Free Savings Balance")
                st.subheader(f"UGX {mem.get('savings_balance', 0):,}")
                st.markdown('</div>', unsafe_allow_html=True)
            with col_m3:
                st.markdown('<div class="card-metric">', unsafe_allow_html=True)
                st.caption("Net Monthly Income")
                st.subheader(f"UGX {mem.get('monthly_income', 0):,}")
                st.markdown('</div>', unsafe_allow_html=True)
            with col_m4:
                st.markdown('<div class="card-metric">', unsafe_allow_html=True)
                st.caption("KYC Verification")
                status_color = "Verified" if mem.get("kyc_status") == "verified" else "Incomplete"
                st.subheader(status_color)
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Policy Checklists
            st.markdown("#### **Policy Eligibility Evaluation**")
            checklist_items = [
                {"Rule": "Membership Duration (>= 6 mos)", "Standard": "SACCO-CREDIT-001 Section 3.1", "Value": f"{mem.get('membership_months')} mos", "Verdict": "PASS" if mem.get("membership_months", 0) >= 6 else "FAIL"},
                {"Rule": "Repayment Term (6 - 24 mos)", "Standard": "SACCO-CREDIT-001 Section 4.3", "Value": f"{mem.get('requested_term_months')} mos", "Verdict": "PASS" if 6 <= mem.get("requested_term_months", 0) <= 24 else "FAIL"},
                {"Rule": "Delinquency / Active Arrears", "Standard": "SACCO-CREDIT-001 Section 3.4", "Value": "Arrears Present" if mem.get("has_arrears") else "Clean Record", "Verdict": "EXCEPTION_REQUIRED" if mem.get("has_arrears") else "PASS"},
                {"Rule": "Level 2 KYC Verification", "Standard": "SACCO-AML-001 Section 2.2", "Value": mem.get("kyc_status", "missing").title(), "Verdict": "PASS" if mem.get("kyc_status") == "verified" else "PENDING_EVIDENCE"},
                {"Rule": "Guarantor Security Pledges", "Standard": "SACCO-CREDIT-001 Section 6.3", "Value": f"{mem.get('number_of_guarantors', 0)} declared", "Verdict": "PENDING_EVIDENCE" if mem.get("number_of_guarantors", 0) > 0 else "FAIL"}
            ]
            st.table(checklist_items)

            # Financial Calculations
            st.markdown("#### **Deterministic Repayment & Affordability Output**")
            p = mem.get("requested_loan", 0)
            r_annual = mem.get("annual_interest_rate", 18.0)
            n = mem.get("requested_term_months", 12)
            r_monthly = (r_annual / 100) / 12

            if n > 0 and r_monthly > 0:
                emi = p * (r_monthly * (1 + r_monthly)**n) / ((1 + r_monthly)**n - 1)
                tot_pay = emi * n
                tot_int = tot_pay - p
                dsr = ((emi + mem.get("existing_monthly_obligations", 0)) / max(mem.get("monthly_income", 1), 1)) * 100

                col_f1, col_f2, col_f3, col_f4 = st.columns(4)
                with col_f1:
                    st.metric("Monthly Installment (EMI)", f"UGX {emi:,.0f}")
                with col_f2:
                    st.metric("Total Interest", f"UGX {tot_int:,.0f}")
                with col_f3:
                    st.metric("Total Repayable", f"UGX {tot_pay:,.0f}")
                with col_f4:
                    dsr_badge = "High Risk (>50%)" if dsr > 50 else "Compliant (<=50%)"
                    st.metric("Debt Service Ratio (DSR)", f"{dsr:.1f}%", dsr_badge)

                # Amortization Table Expander
                with st.expander("View Detailed Month-by-Month Amortization Schedule"):
                    schedule_rows = []
                    bal = float(p)
                    for m_idx in range(1, int(n) + 1):
                        i_due = bal * r_monthly
                        p_due = emi - i_due
                        bal -= p_due
                        schedule_rows.append({
                            "Month": m_idx,
                            "Opening Principal (UGX)": f"{bal + p_due:,.0f}",
                            "Principal (UGX)": f"{p_due:,.0f}",
                            "Interest (UGX)": f"{i_due:,.0f}",
                            "Installment (UGX)": f"{emi:,.0f}",
                            "Closing Principal (UGX)": f"{max(bal, 0):,.0f}"
                        })
                    st.dataframe(schedule_rows, use_container_width=True)

            # Retrieved SACCO Policy Evidence Expander
            st.markdown("#### **Retrieved SACCO Policy Evidence & Legal Standards**")
            policy_snippets = extract_case_policy_evidence(trace)
            if policy_snippets:
                for ps in policy_snippets:
                    topic = ps.get("topic", "General").title()
                    src_id = ps.get("source_id", "POLICY")
                    doc = ps.get("doc", "SACCO Document")
                    sec = ps.get("section", "General")
                    text = ps.get("text", "")
                    with st.expander(f"**{topic} Rule:** {doc} — {sec} (`{src_id}`)", expanded=True):
                        st.info(text)
            else:
                st.caption("No direct policy snippets extracted for this case state.")

            # Statutory Human Review Disclaimer
            st.markdown("""
            <div class="disclaimer-box">
                <b>STATUTORY GOVERNANCE NOTICE:</b> This case pack has been assembled by the SACCO Member-Case Preparation Agent. 
                Pursuant to UMRA Regulations and SACCO Bylaws, this is an illustrative brief for staff evaluation. 
                The agent possesses <b>NO AUTHORITY</b> to approve, decline, or disburse loans. Final decision rests with the Credit Committee.
            </div>
            """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# TAB 2: AGENT COGNITIVE TRACE EXPLORER
# -----------------------------------------------------------------------------
with tab_trace:
    if not trace:
        st.write("No active execution trace to display.")
    else:
        st.markdown(f"### **Bounded Cognitive Trace: `{trace.case_id}`**")
        st.caption(f"Member ID: {trace.member_id} | Iterations: {len(trace.steps)} of {MAX_ITERATIONS}")

        for s in trace.steps:
            step_num = s.get("step")
            step_name = s.get("name", "Execution Step")
            with st.expander(f"**Step {step_num}: {step_name}**", expanded=True):
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    st.markdown("**Sense (Context Acquired):**")
                    st.info(s.get("sense", "N/A"))
                    st.markdown("**Plan (Action Formulated):**")
                    st.success(s.get("plan", "N/A"))
                with col_c2:
                    st.markdown("**Act (Approved Tool Invocation):**")
                    st.code(s.get("act", "None (Direct reasoning)"))
                    st.markdown("**Observe (Tool Return Payload):**")
                    obs_val = s.get("observe")
                    if isinstance(obs_val, (dict, list)):
                        st.json(obs_val)
                    elif obs_val is not None:
                        st.info(str(obs_val))
                    else:
                        st.caption("No return output recorded.")

        stop_reason = get_trace_stop_reason(trace)
        if stop_reason:
            st.warning(f"**Stop Condition Triggered:** {trace.status} — {stop_reason}")


# -----------------------------------------------------------------------------
# TAB 3: HUMAN APPROVAL GATE
# -----------------------------------------------------------------------------
with tab_governance:
    st.markdown("### **Human Approval Gate**")
    st.caption("Human Authority Gate • Safety Invariant 3 Demonstration")

    if not trace:
        st.info("Run a case preparation to review and adjudicate.")
    else:
        case_data = st.session_state.memory_store.get_case(trace.case_id)
        existing_decision = case_data.get("committee_decision") if case_data else None

        if existing_decision:
            st.error(
                f"**CASE CONCLUDED:** This case was finalized with decision: "
                f"**{existing_decision.get('decision')}** on {existing_decision.get('timestamp')}.\n\n"
                f"*Decided by:* `{existing_decision.get('decided_by')}`\n\n"
                f"*Rationale:* {existing_decision.get('rationale')}\n\n"
                f"**Safety Invariant 3 in effect:** The automated agent cannot reopen or alter this decision."
            )
        else:
            st.write(f"Record human decision for **Case `{trace.case_id}`** (Applicant: `{trace.member_id}`):")
            with st.form("human_approval_decision_form"):
                comm_member = st.text_input("Approving Officer / Committee Member ID", value="COMM-CHAIR-01")
                decision_choice = st.selectbox("Governance Action", ["APPROVED", "REJECTED", "DEFERRED"])
                rationale_text = st.text_area("Decision Notes & Conditions", placeholder="e.g. Approved subject to spousal consent and title deed deposit...")
                submit_decision = st.form_submit_button("Commit Human Approval Decision")

                if submit_decision:
                    if not rationale_text.strip():
                        st.error("Decision notes/rationale are mandatory under UMRA supervisory standards.")
                    else:
                        st.session_state.memory_store.record_committee_decision(
                            case_id=trace.case_id,
                            decision=decision_choice,
                            decided_by=comm_member,
                            rationale=rationale_text
                        )
                        st.success(f"Final human decision '{decision_choice}' permanently recorded in persistent memory!")
                        st.rerun()


# -----------------------------------------------------------------------------
# TAB 4: INTERACTIVE POLICY RAG EXPLORER
# -----------------------------------------------------------------------------
with tab_rag:
    st.markdown("### **Grounded RAG Knowledge & Policy Engine**")
    st.caption("Semantic Vector & Keyword Retrieval over 20 Approved UMRA & SACCO Documents")

    if not RAG_AVAILABLE:
        st.warning(f"RAG Pipeline initialization notice: {RAG_ERROR if 'RAG_ERROR' in locals() else 'Missing dependencies'}")
    else:
        query_input = st.text_input("Ask a Policy Question to the Grounded RAG Corpus:", placeholder="e.g. What is the maximum loan multiplier for agricultural loans?")
        if st.button("Search Policy Corpus"):
            if query_input.strip() and st.session_state.rag_pipeline:
                with st.spinner("Searching 20 approved SACCO policy documents..."):
                    results = st.session_state.rag_pipeline.retrieve_evidence_for_query(query_input, top_k=3)
                    if not results:
                        st.warning("INSUFFICIENT EVIDENCE: No matching policy clause found above threshold.")
                    else:
                        for idx, ev in enumerate(results):
                            st.markdown(f"#### **Result {idx+1}: {ev.chunk.document_title} ({ev.chunk.version})**")
                            st.caption(f"Source ID: `{ev.chunk.source_id}` | Section: `{ev.chunk.section_heading}` | Relevance Score: `{ev.score:.3f}`")
                            st.info(ev.chunk.content)
                            st.markdown("---")
            else:
                st.write("Enter a query to search.")

    st.markdown("#### **Corpus Source Provenance Registry**")
    st.caption("External Laws & Regulations separated from Internal Institutional Policies")
    with st.expander("View Top Registered Policies in /RAG"):
        st.markdown("""
        * **`UMRA-REG-001`**: Tier 4 Regulatory Guidance for SACCOs (External Law)
        * **`UMRA-SACCO-REG-003`**: Tier 4 SACCO Regulations 2020 S.I. 81/2020 (External Law)
        * **`SACCO-BYLAW-001`**: Registered SACCO Bylaws (Internal Constitution)
        * **`SACCO-CREDIT-001`**: Credit Policy and Lending Procedures Manual (Internal Policy)
        * **`SACCO-AML-001`**: AML/CFT & KYC Compliance Policy (Internal Policy)
        * **`SACCO-RATES-001`**: Board-Approved Interest & Fee Schedule (Internal Rate Tariff)
        """)


# -----------------------------------------------------------------------------
# TAB 5: IMMUTABLE AUDIT LOG
# -----------------------------------------------------------------------------
with tab_audit:
    st.markdown("### **Immutable Execution Audit Trail**")
    st.caption("Traceability Telemetry • Timestamped Tool Calls & Cache Invocations")

    if not trace or not trace.audit_log:
        st.write("No audit entries recorded.")
    else:
        audit_entries = trace.audit_log.entries
        st.table([
            {
                "Timestamp": e.get("timestamp", "N/A"),
                "Tool": e.get("tool", "N/A"),
                "Source": e.get("source", "tool_execution"),
                "Inputs": str(e.get("inputs", {})),
                "Result Status": "SUCCESS" if (isinstance(e.get("result"), dict) and e.get("result").get("record_found", True) and not e.get("result").get("error")) else "FLAGGED"
            }
            for e in audit_entries
        ])

        # Download Full Trace
        st.download_button(
            label="Export Trace Transcript (TXT)",
            data=trace.to_text(),
            file_name=f"trace_{trace.case_id}.txt",
            mime="text/plain"
        )
