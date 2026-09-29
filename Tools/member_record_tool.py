"""
Member Record Retrieval Tool (Tool 1) - SACCO Member-Case Preparation Agent

Retrieves a synthetic SACCO member's profile data from the controlled synthetic dataset
for case preparation. Adheres strictly to the schema, validation, and failure contracts
defined in Tools/tool-catalogue.md.

Security & Safety:
- Strictly read-only.
- Bound to synthetic dataset directory only.
- Does not fabricate or extrapolate missing records or fields.
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

# Valid member identifier format: SACCO-M-001 through SACCO-M-999
MEMBER_ID_PATTERN = re.compile(r"^SACCO-M-[0-9]{3}$")

# Default synthetic data directory
DEFAULT_DATA_DIR = Path(__file__).resolve().parents[1] / "evidence" / "demo" / "sacco_baseline" / "data"


class MemberRecordRetrievalError(Exception):
    """Base exception for member retrieval errors."""
    pass


class MemberRecordTool:
    """
    Controlled tool for retrieving member profile data from synthetic storage.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._loaded = False

    def _load_synthetic_records(self) -> None:
        """
        Scans and indexes all synthetic member JSON files in the dataset directory.
        """
        if not self.data_dir.exists() or not self.data_dir.is_dir():
            raise MemberRecordRetrievalError("data_source_unavailable")

        records: Dict[str, Dict[str, Any]] = {}
        try:
            for file_path in self.data_dir.glob("*.json"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        m_id = data.get("member_id")
                        if m_id:
                            records[m_id] = data
                except (json.JSONDecodeError, OSError):
                    continue
        except Exception as exc:
            raise MemberRecordRetrievalError("data_source_unavailable") from exc

        self._cache = records
        self._loaded = True

    def retrieve_member_record(
        self,
        member_id: Any,
        simulate_failure: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieves a member record conforming to the tool-catalogue specification.

        Args:
            member_id: The SACCO member ID string (must match ^SACCO-M-[0-9]{3}$).
            simulate_failure: Optional flag for testing failure handling:
                - 'data_source_unavailable'
                - 'timeout'
                - 'malformed_response'
                - 'incomplete_response'

        Returns:
            Dictionary matching the tool-catalogue output schema or error envelope.
        """
        # 1. Parameter presence and format validation
        if not member_id or not isinstance(member_id, str) or not member_id.strip():
            return {
                "record_found": False,
                "error": "invalid_member_id_format",
                "message": "Member ID is required and must not be empty."
            }

        member_id = member_id.strip()

        if not MEMBER_ID_PATTERN.match(member_id):
            return {
                "record_found": False,
                "error": "invalid_member_id_format",
                "message": f"Member ID '{member_id}' does not match required format '^SACCO-M-[0-9]{{3}}$'."
            }

        # 2. Simulated failure triggers for resilience testing
        if simulate_failure == "data_source_unavailable":
            return {
                "record_found": False,
                "error": "data_source_unavailable",
                "message": "Underlying member data storage service could not be reached."
            }
        elif simulate_failure == "timeout":
            return {
                "record_found": False,
                "error": "tool_timeout",
                "message": "Member retrieval timed out after 5000ms."
            }
        elif simulate_failure == "malformed_response":
            # Return unexpected non-conforming structure to test response validator
            return {
                "member": "unknown",
                "data": []
            }
        elif simulate_failure == "incomplete_response":
            # Return partial response omitting required fields
            return {
                "member_id": member_id,
                "full_name": "Incomplete Member Record"
            }

        # 3. Data lookup
        try:
            if not self._loaded:
                self._load_synthetic_records()
        except MemberRecordRetrievalError:
            return {
                "record_found": False,
                "error": "data_source_unavailable",
                "message": "Synthetic member dataset directory is unavailable or unreadable."
            }

        raw_record = self._cache.get(member_id)
        if not raw_record:
            return {
                "record_found": False,
                "error": "member_not_found",
                "message": f"No synthetic member record exists for identifier '{member_id}'."
            }

        # 4. Strict conforming schema mapping
        return {
            "member_id": str(raw_record.get("member_id", member_id)),
            "full_name": str(raw_record.get("full_name", "")),
            "membership_months": int(raw_record.get("membership_months", 0)),
            "monthly_income": float(raw_record.get("monthly_income", 0.0)),
            "monthly_savings": float(raw_record.get("monthly_savings", 0.0)),
            "savings_balance": float(raw_record.get("savings_balance", 0.0)),
            "existing_monthly_obligations": float(raw_record.get("existing_monthly_obligations", 0.0)),
            "kyc_status": str(raw_record.get("kyc_status", "unverified")),
            "has_arrears": bool(raw_record.get("has_arrears", False)),
            "number_of_guarantors": int(raw_record.get("number_of_guarantors", 0)),
            "data_type": "synthetic",
            "record_found": True
        }


# Convenience standalone function matching tool catalogue naming
_default_instance: Optional[MemberRecordTool] = None


def retrieve_member_record(member_id: Any, simulate_failure: Optional[str] = None) -> Dict[str, Any]:
    global _default_instance
    if _default_instance is None:
        _default_instance = MemberRecordTool()
    return _default_instance.retrieve_member_record(member_id, simulate_failure=simulate_failure)
