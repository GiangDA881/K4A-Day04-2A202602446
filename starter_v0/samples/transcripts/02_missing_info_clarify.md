### 2. File `02_missing_info_clarify.md`
**Nội dung cần dán:**
```markdown
# Kịch bản 2: Thiếu thông tin & Ép dùng Clarify (Missing-info)
**Mô tả:** Đảm bảo agent không tự đoán (hallucinate) thông tin hoặc gọi tool tạo ticket khi user cung cấp thiếu dữ liệu. Agent buộc phải gọi tool `clarify` để hỏi thêm.

**User:** Tạo giúp tôi một cái ticket báo lỗi mạng nhé.

**[Tool Call]** `clarify`
```json
{
  "question": "Bạn vui lòng cung cấp thêm chi tiết về sự cố mạng (ví dụ: không bắt được Wi-Fi, hay mạng chập chờn) và khu vực bạn đang ngồi để tôi ghi nhận vào ticket nhé."
}
[Tool Result] clarify

JSON
{
  "result": "User has been asked for clarification."
}
Assistant: Bạn vui lòng cung cấp thêm chi tiết về sự cố mạng (ví dụ: không bắt được Wi-Fi, mạng có dây chập chờn) và khu vực bạn đang ngồi để tôi có thể ghi nhận chính xác vào ticket nhé.