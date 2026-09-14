# Kế Hoạch Phân Công Nhiệm Vụ Nhóm — Lab Day 04 IT Helpdesk Agent

> **Repository nộp bài:** [https://github.com/Gisgod8811/K4-DAY04-2A202602446](https://github.com/Gisgod8811/K4-DAY04-2A202602446)  
> **Cấu trúc nhóm:** Phương án Mở rộng — 5 thành viên (Song song hóa công việc)

---

## 👥 1. Danh Sách & Phân Vai Thành Viên

| STT | Thành viên | MSSV | GitHub Username | Vai trò chính | Trách nhiệm cốt lõi |
|---|---|---|---|---|---|
| **1** | **Nguyễn Xuân Trường Giang** | 2A202602446 | `Gisgod8811` | **A (Team Lead / Prompt Architect)** | System Prompt, Context carry-over, Versioning & Git Merge |
| **2** | *doanhnhan4605@gmail.com* | *(Cập nhật)* | *(Cập nhật)* | **B (Tool & Schema Engineer)** | Tools Schema (`tools.yaml`), Chuẩn hóa Enums/Args, Tavily |
| **3** | *nguyennhansam0307@gmail.com* | *(Cập nhật)* | *(Cập nhật)* | **C (Eval & Red-Team Author)** | Viết 10 cases `eval_group.json`, Test 12 Adversarial attacks |
| **4** | *haidao2004bt@gmail.com* | *(Cập nhật)* | *(Cập nhật)* | **D (UI & Report Coordinator)** | Live Chat Streamlit UI, Kịch bản demo, Chủ trì `REPORT.md` |
| **5** | *tronghoanpth2101@gmail.com* | *(Cập nhật)* | *(Cập nhật)* | **E (Security & Bonus Tool)** | Chống Data Leakage (Tavily), Guardrails ticket, Code 1 Bonus Tool |

---

## 📋 2. Chi Tiết Nhiệm Vụ & Sản Phẩm Bàn Giao (Deliverables)

### 🔹 Thành viên A: Nguyễn Xuân Trường Giang (Lead / Prompt Architect)
- **File phụ trách chính:**
  - `starter_v0/artifacts/system_prompt.md`
  - `starter_v0/artifacts/version_log.csv`
  - Quản trị repo chung: merge Pull Requests, giải quyết conflict.
- **Nhiệm vụ cụ thể:**
  1. Tinh chỉnh `system_prompt.md` qua từng version: quy định rõ ranh giới hành động, nguyên tắc không đoán identifier (`user_id`, `asset_tag`).
  2. Thiết lập cơ chế xử lý context carry-over (người dùng đổi ý, chỉnh sửa thông tin ở lượt chat sau).
  3. Định dạng chuẩn hóa câu trả lời (JSON, format incident report).
  4. Quản lý vòng lặp phiên bản (`v0` -> `v1` -> `v2`...), tính version hash và ghi chép `version_log.csv`.

---

### 🔹 Thành viên B: doanhnhan4605 (Tool & Schema Engineer)
- **File phụ trách chính:**
  - `starter_v0/artifacts/tools.yaml`
  - Kiểm tra tương thích với `starter_v0/tools/`
- **Nhiệm vụ cụ thể:**
  1. Chuẩn hóa toàn bộ schema của 9 công cụ trong `tools.yaml`: mô tả rõ chức năng (`description`), ràng buộc kiểu dữ liệu, bắt buộc các tham số (`required`).
  2. Bổ sung `enum` cho các trường có tập giá trị cố định (ví dụ tên dịch vụ: VPN, SSO, Email...).
  3. Đồng bộ chuẩn xác tên tool, tên tham số giữa `tools.yaml` và code thực thi trong `starter_v0/tools/`.
  4. Cấu hình và kiểm thử tích hợp `search_device_info` với Tavily API key.

---

### 🔹 Thành viên C: nguyennhansam0307 (Eval & Red-Team Author)
- **File phụ trách chính:**
  - `starter_v0/data/eval_group.json`
  - Chạy và ghi log `starter_v0/data/eval_adversarial.json`
- **Nhiệm vụ cụ thể:**
  1. Tác giả 10 testcases độc quyền của nhóm trong `eval_group.json` (từ `G01` đến `G10`), bao phủ đủ các dạng: single-tool, multi-tool, multi-turn, confirmation flow.
  2. Chạy kiểm thử bộ 12 ca tấn công đối kháng (`eval_adversarial.json`: prompt injection, jailbreak, ép gọi tool ngoài quyền hạn).
  3. Trích xuất metric đánh giá (Accuracy, Routing Error Rate, Argument Error Rate) trước và sau khi tối ưu prompt/tools.

---

### 🔹 Thành viên D: haidao2004bt (UI & Report Coordinator)
- **File phụ trách chính:**
  - `starter_v0/artifacts/REPORT.md`
  - App UI demo (Streamlit / HTML Chat Dashboard)
  - `starter_v0/samples/transcripts/`
- **Nhiệm vụ cụ thể:**
  1. Xây dựng giao diện tương tác Live Chat (bằng Streamlit hoặc HTML/Flask) để người dùng có thể chat trực tiếp với IT Helpdesk Agent.
  2. Chạy thử nghiệm các kịch bản demo tiêu biểu, lưu lại transcript hội thoại mẫu đầy đủ log tool calls.
  3. Chủ trì biên soạn và hoàn thiện file `REPORT.md` theo cấu trúc yêu cầu của giảng viên, tổng hợp kết quả từ thành viên A, B, C, E.

---

### 🔹 Thành viên E: tronghoanpth2101 (Security & Bonus Tool Engineer)
- **File phụ trách chính:**
  - `starter_v0/company_policy/`
  - Thư mục tool mới: `starter_v0/tools/<bonus_tool>/`
  - Kiểm thử an toàn rò rỉ dữ liệu
- **Nhiệm vụ cụ thể:**
  1. **Data Leakage & Boundary:** Rà soát và đảm bảo agent không bao giờ gửi thông tin nội bộ (ID nhân viên, IP, cấu hình bảo mật) ra external service (Tavily).
  2. **Ticket Guardrails:** Đảm bảo hành động `create_ticket` bắt buộc phải có bước xác nhận rõ ràng (`clarify`), ngăn chặn tuyệt đối việc sinh ticket rác/sai sót.
  3. **Bonus Tool (Cộng điểm):** Thiết kế và code thêm 01 Bonus Tool thực tế (ví dụ: `network_ping_diagnostic` hoặc `password_reset_dispatch`), khai báo vào `tools.yaml` và `tools/__init__.py`.

---

## 🚀 3. Quy Trình Phối Hợp Git Chuẩn (Tránh Conflict)

Mỗi thành viên làm việc độc lập trên branch cá nhân của mình để đảm bảo có commit ghi nhận đóng góp:

```powershell
# 1. Clone repository về máy
git clone https://github.com/Gisgod8811/K4-DAY04-2A202602446.git
cd K4-DAY04-2A202602446

# 2. Tạo branch riêng theo username của mình
git switch -c contrib/<github-username>

# 3. Làm bài, kiểm tra file thay đổi
git status

# 4. Commit bằng danh tính Git cá nhân
git add <các-file-thay-đổi>
git commit -m "feat(scope): mô tả ngắn gọn phần việc đã hoàn thành"

# 5. Push branch lên GitHub và tạo Pull Request vào main
git push -u origin contrib/<github-username>
```

> **Lưu ý quan trọng của bài Lab:**  
> Mỗi thành viên **bắt buộc phải có ít nhất 01 commit mang tên mình** xuất hiện trong lịch sử git của branch `main` khi nộp bài trên VLearn.
