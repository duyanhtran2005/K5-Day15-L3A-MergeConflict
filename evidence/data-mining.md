# Đào data — cách đếm và kết quả

> Điền ở guide bước 1.2. Ôn lại: ngày 2, ngày 6 · lab ngày 2, lab ngày 6.
> Không đào data thì xoá file này. Script / công thức đếm để trong repo (vd `evidence/count.py` hoặc ghi công thức Sheets ngay dưới), người khác chạy lại phải ra cùng số.
> Repo chỉ chứa số đã tổng hợp và vài dòng ví dụ — không chép lại nguyên file data.

## 1. Cách đếm — viết TRƯỚC khi chạy

Mục này ghi lại phương pháp từ [báo cáo quan sát Discord](data-mining-yeu-cau-01.md).

- Data dùng: Mẫu ảnh trao đổi về lab trên Discord từ 10–25/11/2026.
- Đếm số câu hỏi hoặc vướng mắc độc lập. Gộp các tin nhắn nối tiếp về cùng một vấn đề. Bỏ lời cảm ơn, emoji và tin nhắn không đặt câu hỏi.
- **Mẫu số:** 9 trường hợp có mã Q01–Q09 trong bảng trường hợp của báo cáo.
- Cách tính lại: Đếm số mã Q khác nhau trong bảng trường hợp. Mỗi mã chỉ tính một lần. Để đếm trường hợp đủ dữ kiện về thời gian chờ, dùng số mã Q trong bảng thời gian chờ của cùng báo cáo.

## 2. Đọc trước, đếm sau

Các hành vi được ghi nhận trong mẫu ảnh:

- Hỏi lại quy định đặt tên repo, hạn nộp hoặc cách nộp lại khi hướng dẫn chưa rõ.
- Nhờ hỗ trợ khi model hoặc nền tảng deploy gặp lỗi hay giới hạn.

## 3. Kết quả

| Đếm gì | x / N | % | Ghi chú |
|---|---|---|---|
| Trường hợp đáp ứng tiêu chí gặp vướng mắc | 9/9 | 100% | Chỉ tính trong mẫu ảnh đã chọn. |
| Trường hợp có đủ mốc hỏi và phản hồi hữu ích đầu tiên | 7/9 | 77,8% | Dùng để mô tả thời gian chờ trong mẫu. |

## 4. ≥5 ví dụ cụ thể (mã dòng / mã đã ẩn danh, không đoán ai là ai)

1. Q01 hỏi cách đặt tên repo khi slide, LMS và hướng dẫn trong buổi lab khác nhau.
2. Q03 hỏi có thể nộp lại khi tên repo thiếu một ký tự.
3. Q06 hỏi mức trừ điểm nếu nộp bài muộn.
4. Q08 hỏi hạn nộp bài trong ngày.
5. Q09 hỏi nền tảng deploy thay thế khi tài khoản bị giới hạn.

Xem [ví dụ nguyên văn đã ẩn danh](data-mining-yeu-cau-01.md#5-năm-ví-dụ-nguyên-văn-đã-ẩn-danh).

## 5. Giới hạn của data

Ảnh do thành viên chọn, có thể thiếu ngữ cảnh và thiên về các ca có vấn đề. Tỷ lệ 9/9 chỉ mô tả mẫu quan sát. Thời gian chờ được tính tới phản hồi hữu ích đầu tiên nhìn thấy trong ảnh.

Nhóm dùng [khảo sát 20 học viên ngoài nhóm](summary.md) làm nguồn bằng chứng chính và dùng mẫu Discord để đối chiếu. Lịch Lab Coach nằm trong [Data Card](../data/DATA_CARD.md) vì đó là dữ liệu thử cho prototype.
