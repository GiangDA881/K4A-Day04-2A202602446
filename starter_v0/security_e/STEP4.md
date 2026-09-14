# Bước 4 — xác nhận ticket tại runtime

## Luồng thực thi

1. Model đề xuất `create_ticket`; runtime kiểm tra payload qua dry-run.
2. `TicketSession` giữ bản nháp trong bộ nhớ riêng của phiên và gọi `clarify`
   với JSON thể hiện đúng summary, priority, asset_id. Runtime dừng lượt đó.
3. Ở lượt người dùng thật kế tiếp, chỉ câu trả lời riêng `yes`, `có`, `co`,
   `đồng ý`, `dong y` mới tạo đúng bản nháp đã hiển thị. Không gọi lại model
   để quyết định payload sau khi người dùng đồng ý.
4. Câu trả lời khác làm mất hiệu lực bản nháp cũ. Nếu model đề xuất bản sửa,
   runtime hiển thị lại và đợi một lượt xác nhận mới.
5. Quyền ghi gắn với payload được tiêu thụ một lần trong context nội bộ;
   `confirmed=True` từ arguments không thể tự cấp quyền. Lỗi ghi cũng tiêu thụ
   xác nhận để tránh tự động retry side effect.

Áp dụng chung cho `HelpdeskAgent.run` và `run_model_tool_loop`. Direct tool call
với Boolean true nhưng không có quyền runtime trả needs_confirmation.
ID ticket dùng UUID, file được mở bằng chế độ exclusive để tránh ghi đè.
Kiểm thử phát hiện cách hash timestamp cũ có thể trùng ID khi ghi rất nhanh.

## Evidence

- `python -B starter_v0/security_e/test_boundaries.py`: **54 PASS, 0 FAIL, 0 ERROR**.
- 6 lỗi runtime từ baseline đều đã được chặn.
- Ca bổ sung kiểm tra luồng hợp lệ trên cả agent/chat, đổi từng trường payload,
  cancellation/JSON giả/câu trả lời hỗn hợp, session isolation, model đổi args
  sau khi trình draft, gọi lặp cùng lượt, draft chứa credential mẫu, lỗi ghi và
  chat không giữ session. Gọi lặp không tái sử dụng xác nhận đã tiêu thụ.
- Control Boolean true được đổi assertion từ tạo file (baseline) sang từ chối
  khi thiếu quyền runtime: đây là thay đổi contract có chủ đích, không phải
  giữ nguyên toàn bộ kỳ vọng kiểm thử cũ.
- Giữ nguyên baseline và step3 JSON; kết quả mới trong `step4_results.json`.
- Mock HTTP/provider, ticket trong thư mục tạm; chưa chạy provider/fixed eval thật.

## Tích hợp và giới hạn cần bàn giao

- **A/D:** có CONFLICT NOTE tại agent/chat/session/tool. Giữ một HelpdeskAgent
  hoặc TicketSession cho mỗi cuộc hội thoại. CLI đã giữ session qua các lượt.
  UI truyền `ticket_session=` vào run_model_tool_loop, hiển thị nguyên câu hỏi
  runtime và xử lý tuần tự một submission mỗi lượt. Không dùng chung session
  cho nhiều người, không nạp trạng thái từ text hoặc tool result.
- Session nằm trong bộ nhớ; restart/mất session sẽ cần trình và xác nhận lại.
  API nhận danh sách messages phải được host tạo từ hội thoại thật; người dùng
  không được tự gắn role hoặc gọi hàm runtime như một trusted host.
- Câu đồng ý dài như “yes but change priority” không được tự suy diễn là xác
  nhận. Khi không chắc, runtime yêu cầu xác nhận lại bản nháp.
- **C/D:** fixed eval tạo agent mới mỗi case và nén lịch sử thành user text.
  E05/E08 trước đây mong tạo ticket trực tiếp sẽ chỉ nhận yêu cầu xác nhận nếu
  chưa có draft runtime. Routing grader vẫn có thể PASS tool call dù chưa ghi
  file: phải đọc tool_results. Không sửa fixed datasets hoặc parser để tin
  confirmation nhúng trong text. Cần transcript nhiều lượt thật làm evidence.
- **B:** schema chưa đổi; bổ sung description rằng confirmed không tự cấp quyền.
- Bộ lọc credential vẫn dựa trên regex; công việc này gia cố quyền ghi, không
  khẳng định chặn mọi dạng secret. Runtime vẫn có thể đề xuất draft sau khi model
  xử lý câu hủy sai, nhưng không ghi nếu chưa có lượt đồng ý mới.
- Bỏ load .env khi import chat; CLI vẫn load trong main. UI cần load môi trường
  tại entry point của app nếu trước đây dựa vào side effect khi import chat.
