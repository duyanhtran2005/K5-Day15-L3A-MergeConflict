# Báo cáo đánh giá — lượt 1 → một cải tiến → lượt 2

> Điền ở guide bước 4.1. Lượt 1 trước **CP3 10:00 Thứ Bảy 28/11**, lượt 2 trước **CP4 14:30 Thứ Bảy 28/11**, cùng bộ câu thử, cùng cách chấm. Chấm ở rubric R5.
> Số lấy từ `python run.py score eval/run-1.csv` (và `run-2.csv`) sau khi điền cột `pass`. **Kết quả thấp ghi thật vẫn đủ điểm.**
> Không được: sửa chuẩn "đạt", bỏ câu thử trượt, sửa `expected` cho khớp output, sửa kết quả lượt đã chạy.

## 1. Kết quả

| Lượt | Run ID | Đạt / tổng | % | thuong | kho | tu_choi | So với chuẩn "đạt" |
|---|---|---|---|---|---|---|---|
| 1 | `run-1@20261128-002906` | 22/24 | 92% | 6/6 (100%) | 11/13 (85%) | 5/5 (100%) | Đạt ngưỡng tổng 80%. Cần đối chiếu các điều kiện còn lại ở §7. |
| 2 | | __/__ | | __/__ | __/__ | __/__ | đạt / chưa |

Lượt 1 dùng `openai/gpt-4o-mini` qua OpenRouter và có 0 lỗi thực thi. [Kết quả từng câu](run-1.csv) · [Trace lượt 1](../traces/run-1.jsonl).

## 2. Lỗi lượt 1 — gom thành nhóm có tên

| Nhóm lỗi | Số câu | Câu |
|---|---|---|
| Thiếu ghi nhận vướng mắc khi hỏi lại | 1 | B15 |
| Tra cứu khi chưa rõ ca học | 1 | B20 |

**Hai câu trượt trong lượt 1**

| Câu | Input | Output | Vì sao sai |
|---|---|---|---|
| B15 | Học viên bị kẹt khi deploy bài lab lên Railway và nhờ Lab Coach hỗ trợ. | “Bạn đang hỏi bài Lab số mấy hoặc tên bài lab nào?” | Hỏi đúng thông tin còn thiếu nhưng chưa ghi nhận vướng mắc deploy Railway theo tiêu chí. |
| B20 | Học viên cần hướng dẫn Lab 13 ngày 05/05/2027 và nhắc đến tài liệu dành cho buổi chiều. | Báo chưa có hướng dẫn trong C204 và chưa xác minh được Lab Coach. | Ca chiều được nhắc đến là ca của tài liệu. Hệ thống đã tra nguồn và lịch trước khi hỏi học viên đang học ca nào. |

## 3. Một lần cải tiến

- Nhắm vào nhóm lỗi: Xác định sai hoặc thiếu ngữ cảnh buổi lab (B20). Tra nhầm ca có thể khiến học viên nhận hướng dẫn sai hoặc hỏi nhầm Lab Coach.
- Đã sửa gì: Tách lớp và phòng khỏi ca học. Khi thiếu thông tin, hỏi đúng dữ kiện còn thiếu trước khi tra. Ca chỉ được nhắc để mô tả tài liệu chưa đủ để xác định ca học của người hỏi.
- Kết quả: Lượt 1 B20 trượt. Chờ chấm Lượt 2 trên cùng 24 câu để ghi kết quả B20 và tỷ lệ đạt chung.
- Câu nào **tệ đi** sau khi sửa: __

## 4. Còn lại

- Lỗi chưa sửa + nguy hiểm thế nào: __
- Nếu có thêm 1 tuần: __
