# Data card — dữ liệu bản chạy thử dùng

> Điền ở guide bước 2.4 (bản đầu ở CP2, đủ ở CP3). Ôn lại: ngày 6 · lab ngày 6. Chấm ở rubric R4.
> Một trang. Mỗi dataset một mục. Dữ liệu chạy thử (bài mẫu, thông báo mẫu, đoạn transcript…) để trong thư mục `data/` này.
> Không commit nguyên tài liệu khoá, dữ liệu cá nhân thật hay nguyên file data BTC cấp — chỉ đoạn trích ngắn, bản viết lại, hoặc số đã tổng hợp.

## Dataset 1 · Tin nhắn thread lab

| | |
|---|---|
| Dùng để làm gì | `search_lab_thread` đọc CSV cục bộ để tìm nguồn đúng thread, bài lab, ngày và ca. Dữ liệu hỗ trợ các ca nguồn đúng, nguồn khác ca, nguồn mâu thuẫn và nguồn ngoài thread. |
| Từ đâu | [lab_thread_messages.csv](lab_thread_messages.csv). Tin nhắn mô phỏng theo các kịch bản trong benchmark của nhóm. URL dùng tên miền `.example`. |
| Xử lý những bước gì | Gán mã tin, thread, bài, ngày và ca. Dùng thread ID do ứng dụng xác định để giới hạn tra cứu. |
| Số dòng / số đoạn | 6 tin trong 5 thread. |
| Phiên bản / ngày lấy | Bản CP2, 27/11/2026. |
| Nhãn | `synthetic` |
| Giới hạn | Tập nguồn nhỏ từ CP2 được dùng lại ở CP4. Link và hạn nộp đều là dữ liệu demo. |

## Dataset 2 · Phân công coach mô phỏng

| | |
|---|---|
| Dùng để làm gì | `lookup_lab_coach` đọc CSV cục bộ để tìm Lab Coach đã được xác nhận đúng lớp, phòng, ngày và ca. B07 kiểm tra khi chưa xác minh được coach. B08 kiểm tra khi có coach mẫu đúng phòng. |
| Từ đâu | [lab_coach_assignments.csv](lab_coach_assignments.csv). Nhóm tham chiếu tình huống phòng chờ xác nhận trong lịch giả lập BTC, sheet `Lịch lab 2604-0805`, L3A Lab 10 chiều 27/04/2027, để dựng LC-01. Nhóm tự dựng LC-02 cho C204 với tên `Coach mẫu A`. |
| Xử lý những bước gì | Chuẩn hóa ngày, lớp, bài lab và ca. Giữ trống phòng và coach của LC-01 vì lịch thiếu phân công theo phòng. Gán nhãn giả cho coach của LC-02. |
| Số dòng / số đoạn | 2 bản ghi. |
| Phiên bản / ngày lấy | Bản CP2, 27/11/2026. |
| Nhãn | `synthetic` |
| Giới hạn | Hai bản ghi mô phỏng một ca đã xác nhận theo phòng và một ca còn chờ xác nhận. CSV chỉ dùng để kiểm thử gợi ý coach và bản nháp tag trong prototype. |
