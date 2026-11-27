# Data card — dữ liệu bản chạy thử dùng

> Điền ở guide bước 2.4 (bản đầu ở CP2, đủ ở CP3). Ôn lại: ngày 6 · lab ngày 6. Chấm ở rubric R4.
> Một trang. Mỗi dataset một mục. Dữ liệu chạy thử (bài mẫu, thông báo mẫu, đoạn transcript…) để trong thư mục `data/` này.
> Không commit nguyên tài liệu khoá, dữ liệu cá nhân thật hay nguyên file data BTC cấp — chỉ đoạn trích ngắn, bản viết lại, hoặc số đã tổng hợp.

## Dataset 1 · Tin nhắn thread lab

| | |
|---|---|
| Dùng để làm gì | Dữ liệu cục bộ dự kiến cho `search_lab_thread` và các ca thử nguồn đúng, nguồn khác ca, nguồn mâu thuẫn và nguồn ngoài thread. |
| Từ đâu | [lab_thread_messages.csv](lab_thread_messages.csv). Tin nhắn mô phỏng theo các kịch bản trong benchmark của nhóm. URL dùng tên miền `.example`. |
| Xử lý những bước gì | Gán mã tin, thread, bài, ngày và ca. Dùng thread ID do ứng dụng xác định để giới hạn tra cứu. |
| Số dòng / số đoạn | 6 tin trong 5 thread. |
| Phiên bản / ngày lấy | Bản CP2, 27/11/2026. |
| Nhãn | `synthetic` |
| Giới hạn | Chỉ bao phủ các tình huống CP2. Link và hạn nộp đều là dữ liệu demo. |

## Dataset 2 · Phân công coach mô phỏng

| | |
|---|---|
| Dùng để làm gì | Dữ liệu cục bộ dự kiến cho `lookup_lab_coach` và ca thử B07–B08. |
| Từ đâu | [lab_coach_assignments.csv](lab_coach_assignments.csv). LC-01 mô phỏng tình huống phòng chờ xác nhận trong lịch giả lập BTC, sheet `Lịch lab 2604-0805`, L3A LAB 10 chiều 27/04/2027. LC-02 do nhóm tự dựng cho C204. |
| Xử lý những bước gì | Chuẩn hóa ngày, lớp, bài lab và ca. Giữ trống phòng và coach của LC-01 vì lịch thiếu phân công theo phòng. Gán nhãn giả cho coach của LC-02. |
| Số dòng / số đoạn | 2 bản ghi. |
| Phiên bản / ngày lấy | Bản CP2, 27/11/2026. |
| Nhãn | `synthetic` |
| Giới hạn | Chỉ có một ca đã xác nhận theo phòng và một ca chưa xác minh. |
