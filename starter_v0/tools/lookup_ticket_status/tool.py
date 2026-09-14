from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[2] / "helpdesk_data" / "ticket_status.json"
TICKET_ID = re.compile(r"LAB-(?:[0-9A-F]{8}|[0-9A-F]{32})", re.ASCII)


def lookup_ticket_status(ticket_id: str = "") -> dict:
    """Read only a fixed local snapshot; never build file paths from input."""
    base = {"tool": "lookup_ticket_status", "source": "educational_ticket_status_snapshot"}
    if not isinstance(ticket_id, str):
        return {**base, "error": "invalid_ticket_id_type"}
    if not ticket_id.strip():
        return {**base, "error": "missing_ticket_id"}
    normalized = ticket_id.strip().upper()
    if not TICKET_ID.fullmatch(normalized):
        return {**base, "error": "invalid_ticket_id"}
    try:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        snapshot = data["snapshot_at"]
        datetime.fromisoformat(snapshot)
        records = data["tickets"]
        if not isinstance(records, list):
            raise ValueError("Invalid records")
        matches = [row for row in records if row["ticket_id"] == normalized]
        if not matches:
            return {**base, "ticket_id": normalized, "found": False, "snapshot_at": snapshot,
                    "message": "Ticket not found in this mock snapshot; its current status is unknown."}
        if len(matches) != 1:
            raise ValueError("Duplicate identifier")
        row = matches[0]
        if row["status"] not in {"open", "in_progress", "resolved", "closed"}:
            raise ValueError("Invalid status")
        if row["priority"] not in {"low", "medium", "high", "critical"}:
            raise ValueError("Invalid priority")
        datetime.fromisoformat(row["updated_at"])
        # Allowlisted output: never return summary, credentials, ownership or logs.
        return {**base, "ticket_id": normalized, "found": True, "status": row["status"],
                "priority": row["priority"], "updated_at": row["updated_at"], "snapshot_at": snapshot}
    except (OSError, ValueError, KeyError, TypeError):
        return {**base, "error": "ticket_status_data_unavailable"}
