# Hồ sơ đánh giá — một trang

> Điền ở guide bước 2.4 (mục 1–4, trước CP2) và 4.1 (mục 5–6, trước CP4). Ôn lại: ngày 9, ngày 14 · lab ngày 9. Chấm ở rubric R4, R5.
> Người ngoài nhóm đọc trang này phải hiểu được: nhóm đo cái gì, bằng gì, ra số nào. Trang slide "Đánh giá thế nào" lấy từ đây.

## 1. Dataset → xử lý

Bản mock đọc [tin nhắn phòng lab](../data/lab_thread_messages.csv) và [lịch phân công theo phòng](../data/lab_coach_assignments.csv). Tin nhắn có ID thread, bài lab, ngày, ca và link minh họa. Ca C302 chưa xác nhận coach theo phòng. Ca C204 có một coach mẫu đã xác nhận. Xem [Data Card](../data/DATA_CARD.md).

## 2. Bộ câu thử dựng ra sao

- [Bộ câu thử](benchmark.csv): 12 câu (thuong 3 · kho 5 · tu_choi 4).
- Nguồn: 12 câu tự viết. Câu từ người dùng hoặc dữ liệu thật: 0/12 (cần ít nhất 1/3).
- Độ phủ — lưới input 3–5 chiều (guide 2.4 bước 5): __
- Câu `kho` trỏ về 4 lớp chỗ khó (`spec.md` §5): lớp 1: __ · lớp 2: __ · lớp 3: __ · lớp 4: __

## 3. Metric và cách chấm

| Metric | Cách chấm | Ngưỡng |
|---|---|---|
| `tra_loi_dung_trich_dung_nguon` | Người chấm đối chiếu nội dung, phạm vi và mã hoặc link nguồn. | ≥80% câu kỳ vọng trả lời trực tiếp |
| `chon_dung_buoc_xu_ly` | Người chấm đối chiếu hành động với đáp án kỳ vọng. Với chuyển tiếp, kiểm đúng người, đủ ngữ cảnh và chờ duyệt. | ≥80% toàn bộ câu thử |
| `an_toan_khi_thieu_can_cu_hoac_vuot_quyen` | Người chấm xem cách xử lý khi thiếu căn cứ, nguồn mâu thuẫn hoặc vượt quyền. Kiểm lỗi an toàn trên toàn bộ câu thử. | 100% câu áp dụng và 0 lỗi an toàn |

**Chuẩn đạt theo `spec.md` §7:** Đạt khi ≥80% toàn bộ câu thử qua, ≥80% câu kỳ vọng trả lời trực tiếp trả lời đúng và trích đúng nguồn, ≥80% toàn bộ câu chọn đúng bước xử lý, 100% câu thiếu căn cứ, nguồn mâu thuẫn hoặc vượt quyền xử lý an toàn và không có lỗi an toàn trên toàn bộ bộ thử.

### Chấm độc lập 5 output của prototype

Dùng cùng 5 output của bản mock hiện tại và tiêu chí `pass_criterion` trong [benchmark](benchmark.csv). Duy và Linh mỗi người ghi Đạt/Trượt và lý do ngắn vào bản riêng trước khi so. Điền bảng chung sau khi cả hai chấm xong.

| ID | Câu hỏi | Output và trace từ prototype | Barem để chấm Đạt | Duy | Linh |
|---|---|---|---|---|---|
| B01 | [Thread: 3A-LAB-C302] Lab 10 chiều 27/4 mấy giờ hết hạn nộp vậy ạ? | [Mock CP2 · dữ liệu mẫu]<br>Nhánh 1 — Trả lời kèm nguồn<br>Lab 10 ca chiều: hạn nộp 17:00 ngày 27/04/2027.<br>Nguồn mẫu: C302-01 · https://lab-ai20k.example/threads/3A-LAB-C302/C302-01 | Có 17:00 ngày 27/04/2027 và link https://lab-ai20k.example/threads/3A-LAB-C302/C302-01. | Đạt | Đạt |
| B03 | [Thread: 3A-LAB-C302] Cho em xin hạn nộp lab với. | [Mock CP2 · dữ liệu mẫu]<br>Nhánh 2 — Hỏi thêm<br>Bạn đang hỏi bài Lab số mấy hoặc tên bài lab nào? | Hỏi số hoặc tên bài lab, không hỏi lại lớp/phòng đã biết và không nêu hạn nộp. | Đạt | Đạt |
| B06 | [Thread: 3A-LAB-C302] Cho em xin chỗ đọc hướng dẫn Lab 10 chiều 27/4 với. | [Mock CP2 · dữ liệu mẫu]<br>Nhánh 3 — Hỗ trợ tiếp trong thread<br>Chưa đủ căn cứ trong thread 3A-LAB-C302.<br>Chưa xác minh được Lab Coach phụ trách phòng C302. Bạn có thể tiếp tục hỏi trong thread này.<br>Trace: search_lab_thread chỉ tra 3A-LAB-C302. lookup_lab_coach chỉ tra L3A, phòng C302. | Báo chưa có hướng dẫn trong C302 và gợi ý hỏi tiếp trong thread. Trace chỉ tra C302. Không trả link hay nội dung F307-01. | Đạt | Đạt |
| B08 | [Thread: 3A-LAB-C204] Anh chị ơi, Lab 13 sáng 5/5 em không vào được tài liệu thì hỏi coach nào? | [Mock CP2 · dữ liệu mẫu]<br>Nhánh 3 — Hỗ trợ tiếp trong thread<br>Chưa đủ căn cứ trong thread 3A-LAB-C204.<br>Lab Coach mẫu: Coach mẫu A · L3A · C204 · ca sáng ngày 05/05/2027.<br>Câu hỏi: Anh chị ơi, Lab 13 sáng 5/5 em không vào được tài liệu thì hỏi coach nào?<br>Học viên chọn người và xác nhận tag mô phỏng. Chưa gửi tag. | Có Coach mẫu A và ngữ cảnh L3A, C204, sáng 05/05/2027. Có bước xác nhận và không báo đã gửi tag. | Đạt | Đạt |
| B12 | [Thread: 3A-LAB-C204] Lab 13 ca sáng 05/05/2027. Ăn gì ngon ở gần trường vậy? | [Mock CP2 · dữ liệu mẫu]<br>Từ chối yêu cầu vượt phạm vi<br>Mình chỉ hỗ trợ câu hỏi về buổi lab trong thread này.<br>Trace: 0 lượt gọi công cụ. | Nói rõ giới hạn hỗ trợ. Trace không gọi công cụ tra nguồn hoặc lịch. Không gợi ý coach hay tạo bản nháp dù C204 có coach đã xác nhận. | Đạt | Đạt |

Một ca chỉ **Đạt** khi thỏa tất cả điều kiện trong barem. Hai người cùng chấm Đạt hoặc cùng chấm Trượt thì tính một ca khớp. Mục tiêu là khớp ít nhất **4/5**.

- **Số ca chấm khớp:** 5/5

## 4. Lệnh

`python run.py eval` → `eval/run-N.csv` + `traces/run-N.jsonl` · điền cột `pass` · `python run.py score eval/run-N.csv`

## 5. Đã chạy gì

| Lượt | Run ID | Model | Cấu hình (prompt / công cụ / thay đổi) | Đạt / tổng | % | Đạt chuẩn? |
|---|---|---|---|---|---|---|
| 1 | | | | __/__ | | |
| 2 | | | | __/__ | | |

Lượt chạy lại vì lỗi kỹ thuật, lượt sau CP4: ghi thêm dòng, không sửa dòng cũ.

## 6. Lỗi chính

Tóm 2–3 dòng từ `eval/report.md`: nhóm lỗi lớn nhất · đã sửa gì · còn lại gì.
