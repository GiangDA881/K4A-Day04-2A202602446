# Bước 3 — gia cố outbound Tavily

## Thay đổi

- Chỉ chấp nhận cặp hãng/model trong catalog công khai local đã duyệt.
  Query được dựng từ chuỗi chuẩn trong catalog, không từ input tùy ý.
- Catalog bao phủ 9 sản phẩm của fixture và ThinkPad T14 dùng trong smoke test;
  hỗ trợ alias Dell/HP phổ biến. Không đọc inventory để xây allowlist lúc chạy.
- Model chưa có trong catalog bị từ chối trước HTTP. Đây là giới hạn chủ động:
  B/E phải review và thêm tên công khai vào `public_products.py` khi mở rộng.
- Giữ chặn ID nội bộ; validation không phản chiếu input bị từ chối vào error.
- Giới hạn số kết quả là integer 1–5; bắt buộc vendor domain, không theo redirect.
- Không trả exception text từ HTTP; đánh dấu mọi trường web là untrusted.
  Bộ lọc marker chỉ hỗ trợ, không chứng minh chống mọi prompt injection.

## Kết quả kiểm thử local

Chạy `python -B starter_v0/security_e/test_boundaries.py` từ root.

| Evidence | PASS | FAIL | ERROR |
|---|---:|---:|---:|
| Baseline gốc, 28 ca | 12 | 16 | 0 |
| 28 ca cũ sau sửa | 22 | 6 | 0 |
| 17 ca bổ sung | 17 | 0 | 0 |
| Tổng bước 3, 45 ca | 39 | 6 | 0 |

10 lỗi outbound cũ đã được chặn trước mock HTTP. Các kiểm thử bổ sung bao phủ
IPv6, dữ liệu mã hóa, location, secret không có nhãn, instruction trong input,
catalog fixture, alias, sản phẩm lạ, max_results, redirect, exception redaction
và domain giả mạo. Tất cả dùng dữ liệu giả, mock HTTP và provider.

6 FAIL còn lại là ticket confirmation runtime, thuộc bước 4; exit code vẫn là 1.
Không gọi Tavily/model thật; chưa kiểm tra API integration, UI hoặc fixed eval.
Giữ nguyên `baseline_results.json`; evidence mới ở `step3_results.json`.

## Ghi chú phối hợp

- B: có comment CONFLICT NOTE ngay tại validation, catalog và TOOL.md.
  Khi tích hợp, bổ sung mô tả catalog và ràng buộc 1–5 vào tools.yaml.
- A: có thể thêm hướng dẫn xử lý `unapproved_public_product` trong prompt;
  không tự biến đổi chuỗi nội bộ để thử vượt validation.
- C/D: dùng số liệu local này đúng phạm vi; không coi là fixed-suite accuracy.
- Chưa sửa system_prompt.md, tools.yaml, registry hoặc runtime ticket ở bước này.
