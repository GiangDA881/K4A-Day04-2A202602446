from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from providers.base import Provider, ToolCall
from tools import TOOL_FUNCTIONS
from ticket_session import TicketSession


@dataclass
class AgentRun:
    text: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_results: list[dict[str, Any]] = field(default_factory=list)


class HelpdeskAgent:
    def __init__(
        self,
        provider: Provider,
        *,
        system_prompt: str,
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
    ) -> None:
        self.provider = provider
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.model = model
        # CONFLICT NOTE (A/D): one agent instance per conversation, not per turn.
        self.ticket_session = TicketSession()

    def run(self, user_messages: list[dict[str, str]], *, tool_choice: Any | None = None) -> AgentRun:
        latest = user_messages[-1] if user_messages else {}
        action = self.ticket_session.begin_turn(latest.get("content", "") if latest.get("role") == "user" else "")
        if action is not None:
            return AgentRun(text=str(action), tool_results=[{"tool": "create_ticket", "result": action}])
        messages = [{"role": "system", "content": self.system_prompt}, *user_messages]
        response = self.provider.complete(
            messages,
            self.tools,
            model=self.model,
            temperature=0.0,
            tool_choice=tool_choice,
        )
        results: list[dict[str, Any]] = []
        for call in response.tool_calls:
            if call.name == "create_ticket":
                result = self.ticket_session.propose(call.args)
                results.append({"tool": call.name, "args": call.args, "result": result})
                if result.get("awaiting_user"):
                    return AgentRun(text=result["question"], tool_calls=response.tool_calls, tool_results=results)
                continue
            func = TOOL_FUNCTIONS.get(call.name)
            if not func:
                results.append({"tool": call.name, "error": "unknown_tool"})
                continue
            try:
                result = func(**call.args)
            except Exception as exc:  # keep eval robust; failures are evidence
                result = {"error": type(exc).__name__, "message": str(exc)}
            results.append({"tool": call.name, "args": call.args, "result": result})
            if isinstance(result, dict) and result.get("awaiting_user"):
                return AgentRun(text=result.get("question"), tool_calls=response.tool_calls, tool_results=results)
        return AgentRun(text=response.text, tool_calls=response.tool_calls, tool_results=results)
