# Thành viên E — chuẩn bị và kiểm chứng baseline

## Bước 1

- Branch đã kiểm tra: `contrib/phanTrongHoan`.
- Git identity hiện tại: `naoh-pt <tronghoanpth2101@gmail.com>`; chưa thay đổi cấu hình.
- Theo xác nhận của thành viên E, system prompt đã thống nhất giữa 5 thành viên.
  Working tree vẫn báo file này modified so với Git HEAD; không ghi đè hoặc stage file đó.
- Bước 1–2 chỉ thêm kiểm thử và tài liệu của E, chưa sửa runtime, prompt hoặc schema.

## Điểm dễ conflict — ghi chú phối hợp khi triển khai tiếp

| File | Phối hợp | Nội dung |
|---|---|---|
| `starter_v0/artifacts/system_prompt.md` | A | Quy tắc confirmation, cancellation, injection; A chủ trì chỉnh prompt. |
| `starter_v0/artifacts/tools.yaml` | B | Boundary description và schema bonus; thống nhất patch trước merge. |
| `starter_v0/tools/__init__.py` | B | Registry bonus và đồng bộ tên/schema. |
| `starter_v0/agent.py`, `starter_v0/chat.py` | A, D | Nếu thêm kiểm chứng confirmation ở runtime, cần giữ CLI/eval/UI nhất quán. |
| `starter_v0/tools/search_device_info/tool.py` | B | E gia cố dữ liệu outbound; B phụ trách Tavily integration. |
| `starter_v0/data/eval_group.json` | C | E cung cấp case; C giữ tổng đúng 10 case, 5 single + 5 multi. |
| `starter_v0/artifacts/REPORT.md` | D | E bàn giao evidence B4a/B5/B6; D tổng hợp. |

Đây là đề xuất phối hợp, chưa phải xác nhận từ các thành viên khác.

## Bước 2 — cách chạy

Từ thư mục gốc repository:

```powershell
python -B starter_v0/security_e/test_boundaries.py
```

Kiểm thử dùng unittest, mock HTTP và provider, chỉ dùng dữ liệu giả lập.
Ticket ghi vào TemporaryDirectory và được dọn sau mỗi test. Không đọc `.env`,
không gọi API thật, không dùng quota và không tạo ticket trong repository.

Assertion diễn tả hành vi an toàn mong muốn. FAIL là evidence lỗi cần xử lý,
không đánh dấu expectedFailure để che lỗi. Baseline gốc giữ nguyên tại
`starter_v0/security_e/baseline_results.json`; từ bước 3, chạy lại ghi vào
`starter_v0/security_e/step4_results.json` ở phiên bản bước 4 hiện tại.
Evidence bước 3 giữ nguyên tại `starter_v0/security_e/step3_results.json`.

Các test runtime cố ý giả lập model trả tool call sai để kiểm tra lớp thực thi
có chặn được hay không. Chúng không đo xác suất model thật vi phạm prompt và
không thay thế fixed adversarial suite hoặc metric của bài lab.
