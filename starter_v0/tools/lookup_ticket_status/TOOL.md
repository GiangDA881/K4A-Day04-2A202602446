---
name: lookup_ticket_status
track: team-built-bonus
kind: local_read
provider: fictional_ticket_status_snapshot
requires_env: []
inputs: [ticket_id]
outputs: [found, ticket_id, status, priority, updated_at, snapshot_at, source]
side_effect: false
---
# lookup_ticket_status

Tra cứu trạng thái ticket đã có theo ID chính xác trong snapshot giả lập local.
Không dùng để tạo ticket, đọc policy hoặc kiểm tra trạng thái dịch vụ IT.
Thiếu ID: agent phải gọi clarify; không đoán ID. Hai ID cần hai lời gọi riêng.

Input chấp nhận LAB- và 8 hoặc 32 ký tự hex, không phân biệt hoa thường.
Không dùng input để dựng path. Output chỉ gồm trạng thái, độ ưu tiên và thời
gian snapshot/cập nhật; không trả summary, owner, asset, log hoặc credential.
Không gọi network, không ghi file và không cần confirmation cho thao tác đọc.

Nguồn duy nhất là `helpdesk_data/ticket_status.json`. Đây là snapshot, không phải
trạng thái thời gian thực. Ticket tạo trong `tickets/` không tự có trong snapshot;
`found=false` nghĩa là không biết trạng thái ở nguồn này, không phải ticket không tồn tại.

Demo: LAB-DE000001 open, LAB-DE000002 in_progress, LAB-DE000003 resolved.
Smoke từ starter_v0:

```powershell
python -B -c "from tools import TOOL_FUNCTIONS; print(TOOL_FUNCTIONS['lookup_ticket_status']('LAB-DE000001'))"
```

CONFLICT NOTE (B/C/D): B đồng bộ declaration/registry; C chọn case từ
`security_e/eval_bonus.json` vào đúng 10 case nhóm; D tích hợp demo thật và report.
