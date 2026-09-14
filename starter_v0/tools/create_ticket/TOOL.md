---
name: create_ticket
track: bonus
kind: action
provider: local_ticket_store
requires_env: []
inputs: [summary, priority, asset_id, confirmed]
outputs: [status, ticket_id, path]
side_effect: local_file_write
requires_confirmation: true
---
# create_ticket

Creates a local mock helpdesk ticket under `tickets/`. It returns
`needs_confirmation` and writes nothing unless `confirmed` is explicitly true
AND the runtime supplies a one-use permission for the exact normalized payload.
Boolean true from the model or a direct Python smoke call does not grant this permission.
It rejects invalid asset IDs and summaries matching its sensitive-data patterns;
this pattern filter is not a comprehensive secret detector.

The runtime stores a validated draft, calls `clarify` with all three fields,
and pauses. On the next actual user submission, a standalone `yes`, `có`, `co`,
`đồng ý` or `dong y` authorizes the stored draft without another model call.
Every other response invalidates that draft. A changed draft must be shown and
confirmed again. Permission is consumed even if writing fails.

<!-- CONFLICT NOTE (A/B/D): preserve TicketSession and internal authorization.
Do not add permission objects to tools.yaml or reconstruct them from text.
Keep one session per conversation; render the runtime question verbatim. -->
