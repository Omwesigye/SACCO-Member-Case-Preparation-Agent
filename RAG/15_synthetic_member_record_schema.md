---
source_id: "SACCO-SYN-001"
title: "Synthetic Member-Record Schema & Specification"
document_type: "Data Architecture Schema"
owner: "AI Engineering & Product Team"
issuing_authority: "Technical Architecture Lead / SACCO Data Officer"
version: "v1.2"
approval_date: "2026-02-01"
effective_date: "2026-02-01"
origin: "Project Testing Asset"
file_name: "15_synthetic_member_record_schema.md"
official_publication_link: "ref://sacco/synth/schema-v1"
access_status: "Approved for RAG prototype"
confidentiality: "Internal / Synthetic Test Data"
review_status: "Verified by Solution Architect"
hash_or_checksum: "sha256:6b553e1a0b3e6c5188f5db99908cfd52a23e129aa240974bfa56a69ef4f85e49"
relevant_sections: "Section 1 (Schema Rationale & Privacy Guarantee), Section 2 (Data Dictionary), Section 3 (JSON Schema Definition), Section 4 (Sample JSON Profile)"
relevance: "Provides the standardized structure for synthetic member profiles queried by the agent during step 2 (Record and policy retrieval)."
---

# Synthetic Member-Record Schema & Specification

## 1. Rationale and Privacy Compliance
Pursuant to [Data Protection Policy Section 4](file:///d:/Sacco-Agent/RAG/10_data_protection_and_information_security_policy.md#4-artificial-intelligence-automated-systems-and-synthetic-data-mandate), no real or identifiable SACCO member personal data is permitted in AI prototype development, evaluation, or demonstrations. This schema defines the structured synthetic member record format retrieved by the agent to contrast against declared application data.

---

## 2. Data Dictionary

| Field Path | Type | Constraints / Format | Description |
| :--- | :--- | :--- | :--- |
| `member_id` | String | Pattern `^M-[0-9]{5}$` | Unique synthetic identifier (e.g., `M-04921`). |
| `full_name` | String | Ugandan realistic name | Synthetic member full name. |
| `nin_synthetic` | String | Pattern `^CM[0-9]{8}[A-Z]{2}$` | Pseudonymized National ID string. |
| `join_date` | Date | ISO `YYYY-MM-DD` | Date admitted into SACCO membership. |
| `membership_status` | String | Enum: `ACTIVE`, `INACTIVE`, `DORMANT` | Current operational membership state. |
| `shares.count` | Integer | $\ge 0$ | Number of ordinary shares owned. |
| `shares.total_value_ugx` | Number | $\text{count} \times 10,000$ | Total paid share capital. |
| `savings.compulsory_ugx`| Number | $\ge 0$ | Compulsory monthly savings balance. |
| `savings.voluntary_ugx` | Number | $\ge 0$ | Demand / withdrawable savings balance. |
| `savings.pledged_ugx`   | Number | $\ge 0$ | Portion encumbered by own loans or guarantees. |
| `savings.free_ugx`      | Number | $(\text{compulsory} + \text{voluntary}) - \text{pledged}$ | Unencumbered savings available for credit. |
| `income.net_monthly_ugx`| Number | $\ge 0$ | Verifiable net monthly earnings. |
| `credit.active_loans`   | Integer | $\ge 0$ | Count of existing active credit facilities. |
| `credit.par_status`     | String | Enum: `PERFORMING`, `WATCH`, `SUBSTANDARD`, `LOSS` | Delinquency classification. |
| `credit.days_past_due`  | Integer | $\ge 0$ | Current arrears in days. |
| `kyc.level`             | Integer | Enum: `1`, `2` | KYC compliance level (2 required for loans). |
| `kyc.pep_flag`          | Boolean | `true` or `false` | Politically Exposed Person indicator. |

---

## 3. JSON Schema Specification (Draft 7)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SACCOSyntheticMemberRecord",
  "type": "object",
  "required": [
    "member_id",
    "full_name",
    "nin_synthetic",
    "join_date",
    "membership_status",
    "shares",
    "savings",
    "income",
    "credit_history",
    "kyc"
  ],
  "properties": {
    "member_id": { "type": "string", "pattern": "^M-[0-9]{5}$" },
    "full_name": { "type": "string" },
    "nin_synthetic": { "type": "string" },
    "date_of_birth": { "type": "string", "format": "date" },
    "phone": { "type": "string" },
    "residence": {
      "type": "object",
      "properties": {
        "village": { "type": "string" },
        "district": { "type": "string" }
      }
    },
    "join_date": { "type": "string", "format": "date" },
    "membership_status": { "type": "string", "enum": ["ACTIVE", "INACTIVE", "DORMANT"] },
    "shares": {
      "type": "object",
      "properties": {
        "count": { "type": "integer", "minimum": 0 },
        "total_value_ugx": { "type": "number", "minimum": 0 }
      },
      "required": ["count", "total_value_ugx"]
    },
    "savings": {
      "type": "object",
      "properties": {
        "compulsory_ugx": { "type": "number" },
        "voluntary_ugx": { "type": "number" },
        "pledged_ugx": { "type": "number" },
        "free_ugx": { "type": "number" }
      },
      "required": ["compulsory_ugx", "voluntary_ugx", "pledged_ugx", "free_ugx"]
    },
    "income": {
      "type": "object",
      "properties": {
        "net_monthly_ugx": { "type": "number" },
        "monthly_living_expenses_ugx": { "type": "number" },
        "source": { "type": "string" }
      },
      "required": ["net_monthly_ugx", "source"]
    },
    "credit_history": {
      "type": "object",
      "properties": {
        "total_loans_completed": { "type": "integer" },
        "active_loans_count": { "type": "integer" },
        "current_principal_outstanding_ugx": { "type": "number" },
        "days_past_due": { "type": "integer" },
        "par_status": { "type": "string", "enum": ["PERFORMING", "WATCH", "SUBSTANDARD", "DOUBTFUL", "LOSS"] },
        "crb_score": { "type": "integer" }
      },
      "required": ["active_loans_count", "days_past_due", "par_status"]
    },
    "kyc": {
      "type": "object",
      "properties": {
        "level": { "type": "integer", "enum": [1, 2] },
        "nin_verified": { "type": "boolean" },
        "lc1_verified": { "type": "boolean" },
        "pep_flag": { "type": "boolean" }
      },
      "required": ["level", "nin_verified", "pep_flag"]
    }
  }
}
```

---

## 4. Benchmark Sample Record: John Okello (M-04921)
```json
{
  "member_id": "M-04921",
  "full_name": "John Okello",
  "nin_synthetic": "CM84021984KL34",
  "date_of_birth": "1984-05-14",
  "phone": "+256 772 400 912",
  "residence": {
    "village": "Rwizi Central",
    "parish": "Buremba",
    "district": "Kazo"
  },
  "join_date": "2024-03-10",
  "membership_status": "ACTIVE",
  "shares": {
    "count": 30,
    "total_value_ugx": 300000
  },
  "savings": {
    "compulsory_ugx": 3600000,
    "voluntary_ugx": 400000,
    "pledged_ugx": 0,
    "free_ugx": 4000000
  },
  "income": {
    "net_monthly_ugx": 2400000,
    "monthly_living_expenses_ugx": 900000,
    "source": "Dairy Farming & Grain Trading"
  },
  "credit_history": {
    "total_loans_completed": 2,
    "active_loans_count": 0,
    "current_principal_outstanding_ugx": 0,
    "days_past_due": 0,
    "par_status": "PERFORMING",
    "crb_score": 724
  },
  "kyc": {
    "level": 2,
    "nin_verified": true,
    "lc1_verified": true,
    "pep_flag": false
  }
}
```
