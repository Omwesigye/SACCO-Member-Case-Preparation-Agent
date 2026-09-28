---
source_id: "SACCO-DATA-001"
title: "Data Protection, Privacy and Information Security Policy"
document_type: "Internal Security Policy"
owner: "Data Protection Officer / Board"
issuing_authority: "SACCO Board of Directors / Registered with Personal Data Protection Office (PDPO) Uganda"
version: "v2.0"
approval_date: "2026-01-12"
effective_date: "2026-02-01"
origin: "SACCO internal document"
file_name: "10_data_protection_and_information_security_policy.md"
official_publication_link: "ref://sacco/sec/data-priv-2026"
access_status: "Approved for RAG prototype"
confidentiality: "Internal / Restricted"
review_status: "Verified by Data Protection Officer"
hash_or_checksum: "sha256:e0b62e4c022f462f8ea3b9e4a3262db94d13e2f558fb695c029dfad1537b0185"
relevant_sections: "Section 2 (Data Processing Principles), Section 3 (Member Consent & Rights), Section 4 (Synthetic Data & AI Prototype Protections), Section 5 (Access Control & Audit Logging)"
relevance: "Mandates synthetic data usage for AI/RAG prototypes, privacy-by-design boundaries, and strict prohibition of real PII exposure."
---

# Data Protection, Privacy and Information Security Policy

## 1. Legal Basis and Regulatory Registration
* **1.1 Statutory Framework:** Operates in full compliance with the **Data Protection and Privacy Act, 2019** and the Data Protection and Privacy Regulations, 2021 of the Republic of Uganda.
* **1.2 PDPO Registration:** The SACCO is officially registered as a Data Controller and Data Processor with the Personal Data Protection Office (PDPO) under the National Information Technology Authority, Uganda (NITA-U).

## 2. Core Data Processing Principles
All member records, employee information, and credit data must be:
1. **Processed lawfully, fairly, and transparently** with express, documented member consent.
2. **Collected for explicit, specified, and legitimate cooperative purposes** (membership administration, credit underwriting, regulatory reporting).
3. **Adequate, relevant, and limited to what is necessary** (Data Minimization).
4. **Accurate and kept up to date**; reasonable steps must be taken to rectify inaccuracies without delay.
5. **Stored only for as long as necessary** to fulfill cooperative and statutory accounting obligations (7-year retention rule under Ugandan law).
6. **Secured against unauthorized processing, accidental loss, destruction, or damage** through robust technical and organizational safeguards.

## 3. Member Rights and Consent Protocols
* **3.1 Express Consent:** No credit inquiry (CRB search), loan processing, or third-party guarantor verification can proceed without an unambiguous, written, or digitally signed Consent Agreement from the data subject.
* **3.2 Member Data Rights:** Every SACCO member possesses the statutory right to:
  * Inspect and obtain a certified copy of their personal data and credit history.
  * Request immediate rectification of incorrect personal information.
  * Withdraw consent for secondary marketing notifications.

## 4. Artificial Intelligence, Automated Systems, and Synthetic Data Mandate
* **4.1 Absolute Ban on Live PII in Prototypes:**
  To guarantee complete privacy during the development, training, evaluation, and piloting of AI-assisted tools (such as the Member-Case Preparation Agent):
  * **No real, identifiable member data (names, actual NINs, phone numbers, real bank records) shall ever be ingested into external models, shared APIs, or test environments.**
  * All prototype development, RAG testing, and demonstration workflows must utilize **100% team-created synthetic profiles**.
* **4.2 Deterministic Gating of Automated Decisions:**
  In compliance with Section 23 of the Data Protection and Privacy Act, 2019, **no automated system or AI agent is permitted to make a binding financial decision, loan refusal, or account alteration without substantive, human review and approval**.

## 5. Access Control and Audit Logging
* **5.1 Role-Based Access Control (RBAC):** Access to member files, savings ledgers, and credit appraisals is strictly restricted according to authenticated employee role:
  * *Loan Officer:* Access only to assigned applicants within branch jurisdiction.
  * *Credit Committee Members:* Access to finalized case packs scheduled for review.
  * *System Administrator:* Technical administration; barred from editing financial ledger records.
  * *Internal Auditor / Supervisory Committee:* Read-only immutable access to all files and audit trails.
* **5.2 Immutable Audit Trail:** Every retrieval, view, edit, or generation action performed by users or automated agents is recorded with an immutable timestamp, user ID, IP address, and hash in the central security log.
