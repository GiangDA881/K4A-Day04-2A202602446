# Bước 5 — bonus lookup_ticket_status

## Bàn giao

- `tools/lookup_ticket_status/`: implementation và TOOL.md.
- `helpdesk_data/ticket_status.json`: 3 ticket giả lập, có timestamp snapshot.
- `tools/__init__.py`, `artifacts/tools.yaml`: đã đăng ký tool thứ 10;
  có CONFLICT NOTE để B giữ phần bonus khi merge.
- `security_e/test_bonus.py`: 9 kiểm thử PASS, 0 FAIL/ERROR.
- Chạy regression `test_boundaries.py`: 54 PASS, 0 FAIL/ERROR.
- `bonus_results.json`, `bonus_mock_transcript.json`: evidence local và chat
  dùng provider giả lập, không khẳng định model thật chọn đúng tool.
- `eval_bonus.json`: 3 case đề xuất cho C, gồm status, missing ID và correction.
  Chưa thêm vào eval_group.json để tránh vượt đúng 10 case nhóm.

## Chạy thử từ root

```powershell
python -B starter_v0/security_e/test_bonus.py
python -B starter_v0/security_e/test_boundaries.py
```

## Kịch bản demo cho D

1. “Ticket LAB-DE000001 có trạng thái gì trong snapshot?” → open, high.
2. “À nhầm, LAB-DE000002.” → in_progress, medium.
3. “Kiểm tra ticket của tôi.” → model cần clarify ID, không tự đoán.
4. “Tra LAB-FFFFFFFF.” → found=false, trạng thái chưa biết trong snapshot.

Các bước trên là kịch bản mong muốn; chỉ demo thứ 2 bằng provider giả lập đã
có transcript. C/D cần chạy UI/model thật ở bước 6 để có routing evidence.

## Giới hạn và bảo mật

- Chỉ đọc fixed fixture, không đọc path do người dùng truyền và không có network.
- Output chỉ cho phép ID, status enum, priority enum, thời gian và source.
  Không trả summary, owner, asset, credential hoặc diagnostics.
- ID thiếu/sai, path traversal, dữ liệu hỏng hoặc trùng ID đều có lỗi rõ ràng.
- Snapshot không tự đồng bộ với tickets/; không suy diễn trạng thái ticket mới.
- Đây là capability mới của nhóm, khác create_ticket có sẵn.

## Việc còn lại để đủ evidence bonus toàn bài

- C chọn case vào group suite, bảo toàn 5 single-turn + 5 multi-turn.
- D demo trong UI và đưa evidence vào REPORT B5.
- A cân nhắc bổ sung routing bonus vào prompt, nhất là context correction.
- Chạy provider/eval thật và review output ở bước 6; chưa thực hiện trong bước 5.
