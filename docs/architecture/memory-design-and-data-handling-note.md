# Memory Design and Data Handling Note

**SACCO Member-Case Preparation Agent — Week 6**

## 1. Purpose and Principle

This note defines what the agent remembers, why, who can see it, how long it is kept, and how it is deleted.

**Guiding principle:** the agent remembers only what a legitimate task needs. Memory exists to help staff work faster and more consistently, never to make or influence a lending decision silently. Any remembered item that is shown to the agent must be labelled with its source and date, and critical values are always re-checked against the current record and recalculated by the deterministic tools.

All data in this prototype is synthetic. The design below is written as if the system were handling real member data, so the controls are in place before any real data could ever be introduced.

## 2. Two Separate Layers

| | Session State (temporary) | Persistent Case History (stored) |
|---|---|---|
| Purpose | Lets the agent track progress inside one run of the workflow | Lets staff and the agent refer back to past work on a case |
| Lifetime | One workflow run only | Retained under the rules in Section 5 |
| Where it lives | In memory during the run | A controlled case-history store (draft records and audit log) |
| Survives a restart | No | Yes |
| Example | iteration count, current step, tool results so far | A completed case pack and its calculation outputs |

Keeping these apart means that nothing from a live run is saved by accident. A value only becomes persistent when it is explicitly written to case history as one of the approved item types in Section 4.

## 3. Session State (Temporary)

| Field | Why it is needed | Cleared when |
|---|---|---|
| member_id / case_id | Identifies the one case being worked on | Workflow ends |
| member_record (working copy) | Source data for policy checks and calculations in this run | Workflow ends |
| policy_evidence | Evidence retrieved for this run, with citations | Workflow ends |
| calculations_completed | Tracks which calculations have run | Workflow ends |
| iteration_count | Enforces the maximum of 6 iterations | Workflow ends |
| status (IN_PROGRESS, READY_FOR_REVIEW, STOPPED_INCOMPLETE, STOPPED_ERROR) | Controls when the agent must stop | Workflow ends |
| missing_fields | Reports what is missing when the agent stops | Workflow ends |

**Rules**
- Session state is scoped to a single case. It is never shared with, or reused for, another member's case.
- The working copy of the member record is discarded when the run ends. Only the approved items in Section 4 are carried forward.
- If a session times out or fails, its state is discarded, not recovered silently.

## 4. Persistent Case History (Justified Memory)

Only the following five item types are stored. Each has a stated reason.

### 4.1 Previous case results (case pack records)
- **What is stored:** case pack ID, member ID, creation timestamp, status (for example DRAFT_READY_FOR_HUMAN_REVIEW), the policy rule outcomes (PASS, FAIL, PENDING_EVIDENCE, EXCEPTION_REQUIRED), and the list of pending items.
- **Why:** staff reopening a case should see what was prepared before, instead of the work being repeated or contradicted.
- **Who can access:** Loan Officer handling the case; Credit Committee members reviewing that case; Auditor (read-only).
- **Retention:** see Section 5.
- **Deletion:** see Section 6.

### 4.2 Completed calculation outputs
- **What is stored:** the calculation type, the inputs used, the results (monthly payment, total interest, total repayment, DSR percentage, savings limit, coverage), the policy version in force, and the date.
- **Why:** it makes the case pack reproducible and auditable, and lets a reviewer see exactly which figures were put in front of them.
- **Important limit:** stored results are reference only. When a case is reopened, the deterministic calculator is run again against the current record. If the new result differs from the stored one, the difference is flagged to the officer instead of the old figure being reused.
- **Who can access:** same as 4.1.

### 4.3 Approved policy versions
- **What is stored:** for each policy document used, the Source ID, document title, version (for example SACCO-CREDIT-001 v3.0), section cited, and the date it was used.
- **Why:** it shows which version of policy a case was prepared under, so a later policy change does not make an older case look wrong.
- **Who can access:** Loan Officer, Credit Committee, Auditor (read-only). Only a System Administrator can add or retire a policy version.
- **Important limit:** if a case is reopened and the policy version has since changed, the agent flags it as stale and re-retrieves current policy. It does not silently apply the older version.

### 4.4 Staff review comments
- **What is stored:** comment text, reviewer identity, role, timestamp, and the case pack ID it relates to.
- **Why:** it keeps the human reasoning attached to the case, which supports accountability and avoids repeated questions.
- **Who can access:** Loan Officer and Credit Committee for that case; Auditor (read-only).
- **Important limit:** comments are shown to staff as history. The agent may display them but must not treat a past comment as an approval, a rejection, or an instruction for a new case.

### 4.5 Audit log entries
- **What is stored:** tool called, inputs, result summary, timestamp, user or session that triggered it, and any human approval request and decision.
- **Why:** it provides full traceability of what the agent did, which is required for the Human Approval Gate and for internal audit.
- **Who can access:** Auditor (read-only) and System Administrator (read-only). Nobody, including the agent, can edit or delete individual entries.

## 5. Retention

| Item | Proposed prototype retention | Basis |
|---|---|---|
| Session state | Discarded at the end of each run (maximum 30 minutes idle) | No reason to keep it |
| Case pack records | 12 months after the case is closed | Staff reference window |
| Calculation outputs | Same as the case pack they belong to | Reproducibility of the case |
| Policy version usage records | Kept for as long as any retained case refers to them | Case traceability |
| Staff review comments | Same as the case pack they belong to | Accountability |
| Audit log | 24 months, append-only | Audit and oversight |

These periods are proposed defaults for the prototype. For real use they would have to be aligned with the SACCO's records-retention policy and any applicable regulatory requirements, which the team has not assessed and which should be confirmed with the institution.

## 6. Deletion

- **Automatic:** when a retention period ends, the record is purged by a scheduled job. Session state is discarded automatically at the end of the run.
- **On request:** an authorized System Administrator can delete a specific case's records (for example a member data deletion request, or a record created in error). Deletion removes the case pack, linked calculation outputs and linked comments.
- **Audit trail of deletion:** the audit log keeps a record that a deletion happened (who, when, which case ID), but not the deleted content.
- **No agent-initiated deletion:** the agent cannot delete or edit stored history. This prevents it from hiding or rewriting its own earlier work.
- **Policy versions in use:** a policy version cannot be deleted while a retained case still references it.

## 7. What Is Deliberately NOT Stored

- Full copies of the member record beyond the fields needed in Section 4 (for example, income and obligations are stored only as inputs to a saved calculation, not as a separate profile).
- Guarantor identities or personal details.
- National ID numbers, addresses, or KYC documents.
- Free-text conversation history between staff and the agent.
- The model's internal reasoning text.
- API keys, tokens or credentials.
- Any data from one member's case in another member's case context.

## 8. Access Control Summary

| Role | Case packs | Calculation outputs | Policy versions | Staff comments | Audit log |
|---|---|---|---|---|---|
| Loan Officer | Read/create (own cases) | Read | Read | Read/add | No |
| Credit Committee | Read (cases under review) | Read | Read | Read/add | No |
| Auditor | Read-only | Read-only | Read-only | Read-only | Read-only |
| System Administrator | Delete (per Section 6) | Delete (per Section 6) | Add/retire versions | Delete (per Section 6) | Read-only |
| AI Agent | Create draft for the active case only | Create for the active case only | Read | Read for the active case only | Append only |

Access is enforced by the application layer using the authenticated user's role. The language model cannot grant itself or anyone else access by what it says or is told.

## 9. How Memory Helps Without Controlling Decisions

**Legitimate uses of memory**
- A reopened case shows the previous draft, the date it was prepared, and the staff comments, so work is not repeated.
- A reviewer can compare an earlier calculation with a new one and see what changed.
- The policy version used is visible, so a case is judged against the policy that applied when it was prepared.

**Safeguards so memory never silently decides anything**
1. **Recompute, don't reuse.** All financial figures are recalculated by the deterministic tools each time. Stored values are shown for comparison only.
2. **Current record wins.** If remembered data conflicts with the current member record, the current record is used and the conflict is flagged to the officer.
3. **Stale policy is flagged.** A changed policy version triggers fresh retrieval and a visible notice.
4. **History is labelled.** Anything drawn from memory is displayed with its source and date, so staff can see it is a past item.
5. **No carried-over decisions.** A previous human decision or comment is never applied automatically to a new case or a new application.
6. **Human gate unchanged.** Memory has no effect on the Human Approval Gate. Approval, rejection and disbursement remain with authorized staff.

## 10. Failure Handling

| Situation | Behaviour |
|---|---|
| Case history store unavailable | The agent proceeds without history and says so. It never invents past results. |
| Stored record is incomplete or corrupt | The record is treated as untrusted, flagged, and not used. |
| Stored case belongs to a different member | Access is refused. Retrieval is always scoped by case ID and member ID. |
| Unauthorized role requests history | Request rejected by the application layer. |
| Retention period passed but record still present | Record is treated as expired and not shown to the agent. |

## 11. Example Stored Case Record (synthetic)

```json
{
  "case_pack_id": "CASE-2026-0001",
  "member_id": "SACCO-M-001",
  "created_at": "2026-10-06T10:15:00Z",
  "status": "DRAFT_READY_FOR_HUMAN_REVIEW",
  "policy_versions_used": ["SACCO-CREDIT-001 v3.0", "SACCO-AML-001 v3.0"],
  "policy_check_results": {
    "LOAN-001-MEMBERSHIP": "PASS",
    "LOAN-001-GUARANTOR": "PENDING_EVIDENCE"
  },
  "calculations": {
    "repayment_schedule": {"monthly_payment": 550080, "total_repayment": 6600960},
    "debt_service_ratio": {"dsr_percentage": 53.3, "within_policy_limit": false}
  },
  "pending_items": ["Guarantor suitability must be confirmed by an authorized officer"],
  "staff_comments": [],
  "requires_human_review": true
}
```

Note that this record holds no ID numbers, addresses or guarantor details. It holds only what is needed to reproduce and review the case.
