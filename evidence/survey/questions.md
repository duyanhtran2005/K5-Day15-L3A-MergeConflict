# Khảo sát hỗ trợ gấp ngoài lớp

- Đối tượng khảo sát là học viên AI20K L3A từng cần hỗ trợ gấp về bài lab khi ở ngoài lớp trong 30 ngày qua.
- Nhóm chia sẻ Google Forms qua nhóm preclass và qua bạn bè. Bản xuất ghi nhận phản hồi trong hai ngày 27–28/11/2026. Nhóm chưa ghi lại giờ mở và chốt form.
- Bản xuất nội bộ ghi nhận 21 phiếu. Linh xác nhận S01–S20 là 20 học viên L3A khác nhau, đều ở ngoài nhóm MergeConflict. S21 chọn “xin nghỉ học” làm mục đích chính nên được giữ trong log và loại khỏi mẫu số phân tích.

[Biểu mẫu khảo sát](https://docs.google.com/forms/d/e/1FAIpQLSflZVIE3eKlAJR0t3xTbJEx8p5rcoODhe2qiGp1qYUexpg4xA/viewform) · [Log phản hồi ẩn danh](results.csv)

## Câu hỏi

Nội dung dưới đây theo thứ tự cột B–J trong bản xuất Google Forms.

| Cột gốc | Câu hỏi | Cột trong CSV |
|---|---|---|
| B | Trong 30 ngày qua, bạn có từng cần hỗ trợ gấp về bài lab L3A khi không có mặt ở lớp không? | `can_ho_tro_gap_30_ngay` |
| C | Việc chính bạn cần giải quyết là gì? | `viec_chinh` |
| D | Bạn đã tìm thông tin hoặc hỏi hỗ trợ ở những đâu? | `kenh_da_dung` |
| E | Lần đó bạn có được yêu cầu tạo ticket không? | `tao_ticket` |
| F | Bạn đã mất thời gian ở những bước nào? | `buoc_mat_thoi_gian` |
| G | Từ lúc bắt đầu tìm hoặc hỏi đến khi có hướng xử lý dùng được, mất bao lâu? | `thoi_gian_den_huong_xu_ly` |
| H | Việc đó ảnh hưởng đến bạn thế nào? | `anh_huong` |
| I | Trong lần gần nhất cần hỗ trợ gấp khi không có mặt ở lớp, bạn đã làm gì và chuyện gì xảy ra sau đó? | `mo_ta_cho_phep_trich` |
| J | Trong lần gần nhất cần hỗ trợ gấp khi không có mặt ở lớp, bạn đã làm gì và chuyện gì xảy ra sau đó? | `mo_ta_bo_sung` |

Hướng dẫn dưới câu hỏi ở cột I được ghi nguyên văn.

> Trả lời trong 1–2 câu. Nếu nhớ, hãy ghi bạn mất thời gian ở bước nào và khoảng bao lâu. Vui lòng bỏ tên, email và mã học viên. Chỉ điền nếu bạn đồng ý cho nhóm trích tối đa một câu đã ẩn danh trong bài hackathon.

Cột J có cùng tiêu đề và để trống trong cả 21 phiếu.

## Cách lưu bản ẩn danh

- Mã S01–S21 đi theo thứ tự dòng 2–22 của bản xuất. Cột `pham_vi` ghi kết quả lọc theo mục đích ở cột C.
- CSV bỏ cột dấu thời gian và giữ các đáp án đã chọn ở cột B–H. Cột mô tả công khai giữ tối đa một câu mỗi phiếu theo phạm vi đồng ý trích dẫn. Nội dung ở S01–S04 là phần tổng hợp từ đáp án đã chọn.
- Dữ liệu dùng để kiểm lại các số đếm nằm trong CSV. Bản xuất Google Forms được lưu nội bộ.
