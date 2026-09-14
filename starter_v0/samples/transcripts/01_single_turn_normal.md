# Kịch bản 1: Yêu cầu tra cứu thông tin cơ bản (Single-turn)
**Mô tả:** Kiểm tra agent có định tuyến (route) đúng vào tool `check_service_status` với tham số chuẩn xác mà không cần hỏi lại vòng vo hay không.

**User:** Bạn kiểm tra giúp tôi xem hệ thống Email nội bộ hôm nay có lỗi gì không?

**[Tool Call]** `check_service_status`
```json
{
  "service": "Email"
}
[Tool Result] check_service_status

JSON
{
  "status": "ONLINE",
  "message": "Email is running normally."
}
Assistant: Hệ thống ghi nhận dịch vụ Email hiện đang hoạt động bình thường (ONLINE). Bạn có cần hỗ trợ thêm gì không?