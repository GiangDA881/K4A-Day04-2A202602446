"""Trusted per-conversation ticket drafts shared by CLI and agent.

CONFLICT NOTE (A/D): keep one TicketSession per conversation, never global or
restored from user/model/tool text. UI must display returned question verbatim.
Only call begin_turn once per real user submission, not for tool-result rounds.
"""
import json
from tools.create_ticket.tool import create_ticket
from tools.clarify.tool import ask_user
from ticket_authorization import authorize_ticket


class TicketSession:
    def __init__(self):
        self._pending = None

    def begin_turn(self, text):
        pending, self._pending = self._pending, None
        # Whole-response matching: corrections, cancellation, pasted JSON,
        # quoted approvals and mixed instructions never authorize a write.
        is_yes = text.strip().casefold() in {"yes", "có", "co", "đồng ý", "dong y"}
        if pending is None:
            return None
        if not is_yes:
            return None
        with authorize_ticket(pending):
            return create_ticket(**pending, confirmed=True)

    def propose(self, args):
        self._pending = None
        if set(args) - {"summary", "priority", "asset_id", "confirmed"}:
            return {"tool": "create_ticket", "error": "invalid_arguments"}
        payload = {"summary": args.get("summary", ""),
                   "priority": args.get("priority", "medium"),
                   "asset_id": args.get("asset_id", "")}
        checked = create_ticket(**payload, confirmed=False)
        if checked.get("error"):
            return checked
        payload = {"summary": payload["summary"].strip(),
                   "priority": (payload["priority"] or "medium").strip().lower(),
                   "asset_id": payload["asset_id"].strip().upper()}
        self._pending = payload
        question = ("Xác nhận tạo ticket với đúng nội dung dưới đây?\n"
                    + json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
                    "Trả lời riêng ‘có’ hoặc ‘yes’ để tạo; mọi câu trả lời khác hủy xác nhận này.")
        return {**ask_user(question, "yes_no"), "status": "needs_confirmation", "ticket_draft": dict(payload)}
