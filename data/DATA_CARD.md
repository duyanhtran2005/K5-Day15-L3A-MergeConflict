# Data card — dữ liệu bản chạy thử dùng

> Điền ở guide bước 2.4 (bản đầu ở CP2, đủ ở CP3). Ôn lại: ngày 6 · lab ngày 6. Chấm ở rubric R4.
> Một trang. Mỗi dataset một mục. Dữ liệu chạy thử (bài mẫu, thông báo mẫu, đoạn transcript…) để trong thư mục `data/` này.
> Không commit nguyên tài liệu khoá, dữ liệu cá nhân thật hay nguyên file data BTC cấp — chỉ đoạn trích ngắn, bản viết lại, hoặc số đã tổng hợp.

## Dataset 1 · `data/lab_knowledge.json` (Kho tri thức hỗ trợ Lab L3A — Track A2)

| | |
|---|---|
| Dùng để làm gì | Nguồn tra cứu cho công cụ `search_lab_announcements`, `lookup_coach_roster`, `build_handoff_draft` và dữ liệu khởi tạo bản nháp mẫu trong UI (`initial_demo_drafts`). |
| Từ đâu | Nhóm tự cấu trúc và viết lại từ các quy định chung công khai trong khung repo (`README.md`, `spec.md`, `TEAMS.md`, `canvas.md`, `docs/connect-model.md`). |
| Xử lý những bước gì | Chuẩn hoá thành JSON gồm `announcements` (gắn mã `[TB-...]`/`[HD-...]` và trạng thái `active`/`expired`), `coach_roster` theo vai trò chức năng và `initial_demo_drafts`; loại bỏ hoàn toàn tên cá nhân, email, SĐT và API key. |
| Số dòng / số đoạn | 6 thông báo (5 `active`, 1 `expired`), 4 đầu mối Coach/Điều phối theo vai trò, 2 bản nháp demo ban đầu. |
| Phiên bản / ngày lấy | 2026-11-27 (Day 15 · bản chạy thử UI Track A2). |
| Nhãn | `synthetic` |
| Giới hạn | Dữ liệu mô phỏng cho bản chạy thử UI & kiểm thử luồng; không chứa lịch phòng Zoom/Zone nội bộ hay tên thật của trợ giảng/học viên ngoài repo công khai; không dùng thay bằng chứng pain trong `evidence/`. |

**Data `synthetic` (nhóm tự sinh):** Do nhóm tự biên soạn từ tài liệu hướng dẫn chung trong repo (không sinh ngẫu nhiên, kiểm tay toàn bộ 6 thông báo và 4 đầu mối để đối chiếu đúng 3 ca demo ở `canvas.md`). Data tự dựng **không phải bằng chứng pain**.
