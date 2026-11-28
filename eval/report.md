# Báo cáo đánh giá — lượt 1 → một cải tiến → lượt 2

> Điền ở guide bước 4.1. Lượt 1 trước **CP3 10:00 Thứ Bảy 28/11**, lượt 2 trước **CP4 14:30 Thứ Bảy 28/11**, cùng bộ câu thử, cùng cách chấm. Chấm ở rubric R5.
> Số lấy từ `python run.py score eval/run-1.csv` (và `run-2.csv`) sau khi điền cột `pass`. **Kết quả thấp ghi thật vẫn đủ điểm.**
> Không được: sửa chuẩn "đạt", bỏ câu thử trượt, sửa `expected` cho khớp output, sửa kết quả lượt đã chạy.

## 1. Kết quả

| Lượt | Run ID | Đạt / tổng | % | thuong | kho | tu_choi | So với chuẩn "đạt" |
|---|---|---|---|---|---|---|---|
| 1 | `run-1@20261128-002906` | 22/24 | 92% | 6/6 (100%) | 11/13 (85%) | 5/5 (100%) | Đạt ngưỡng tổng 80%. Cần đối chiếu các điều kiện còn lại ở §7. |
| 2 | `run-2@20261128-092151` | 24/24 | 100% | 6/6 (100%) | 13/13 (100%) | 5/5 (100%) | Đạt theo barem đã chốt. |

Cả hai lượt dùng cùng 24 câu và cùng tiêu chí chấm, với 0 lỗi thực thi mỗi lượt. Lượt 1 ghi model `openai/gpt-4o-mini` qua OpenRouter. Lượt 2 ghi model `gpt-4o-mini`. [CSV lượt 1](run-1.csv) · [Trace lượt 1](../traces/run-1.jsonl) · [CSV lượt 2](run-2.csv) · [Trace lượt 2](../traces/run-2.jsonl).

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

- Nhắm vào nhóm lỗi: Hỏi làm rõ khi thiếu ngữ cảnh lab (B15, B20). Bỏ qua vướng mắc khiến học viên có thể phải kể lại. Tra nhầm ca có thể dẫn đến hướng dẫn sai hoặc gợi ý nhầm Lab Coach.
- Đã sửa gì: Giữ vướng mắc và dữ kiện học viên đã nêu, rồi hỏi đúng phần còn thiếu trước khi tra. Ca dùng để mô tả tài liệu không được dùng làm ca học của người hỏi. Thay đổi có trong `77cda2b` và `c41a104`.
- Kết quả: Nhóm câu này tăng từ 0/2 lên 2/2. B15 ghi nhận lỗi deploy Railway rồi hỏi bài lab. B20 giữ Lab 13 và ngày 05/05/2027 rồi hỏi ca học. Cả hai có `tool_calls=0`. Tổng tăng từ 22/24 (92%) lên 24/24 (100%).
- Câu tệ đi sau khi sửa: 0/24 câu chuyển từ đạt sang trượt.

## 4. Còn lại

- Lượt 2 chấm đạt cả 24 câu trong bộ hiện tại.
- Nếu có thêm 1 tuần: Kiểm tra thêm các lượt hỏi nối tiếp khi học viên đính chính ngày hoặc ca để xem trợ lý giữ đúng bài và vướng mắc ban đầu.
