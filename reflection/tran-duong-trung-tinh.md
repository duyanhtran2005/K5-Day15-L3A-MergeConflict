# Reflection — Trần Dương Trung Tính

> Làm ở guide bước 5.3. Mỗi người một file: chép file này thành `reflection/<ten-khong-dau>.md` (viết thường, không dấu). Hạn: **23:59 Thứ Bảy 28/11**. Mỗi câu 3–6 dòng.

1. Vai trò + phần mình làm (trỏ tới file / commit):
   Mình phụ trách toàn bộ phần kỹ thuật bản chạy thử, từ prototype 3 nhánh (`167da7b`, `252e494`) đến nối model thật và đo token từ API trong [ai.py](../codebase/ai.py) (`4d07593`, `85ba06e`).
   Mình thiết kế luồng đánh giá nguồn và các lớp chặn phạm vi thread, lịch Lab Coach theo phòng/ngày/ca ở [agent.py](../codebase/agent.py), kèm kiểm tra kiểu dữ liệu và chặn lệch dữ kiện nguồn (`2f4a869`).
   Sau Lượt 1, mình trực tiếp sửa lỗi hỏi lại ngữ cảnh ở `B15`, `B20`, `B13` (`c41a104`), rồi chạy [Lượt 2](../eval/run-2.csv) (`run-2@20261128-092151`) và chấm 6 câu phần mình đạt 6/6 (`c12c27d`).

2. AI hỗ trợ mình thế nào (việc gì, công cụ gì, chỗ nào phải sửa lại output AI):
   Mình chỉ dùng Codex để gợi ý khung code và rà lại với đặc tả, còn GPT-4o mini đảm nhận đánh giá căn cứ trong thread; toàn bộ kiến trúc chặn rủi ro và kiểm thử đều do mình quyết định.
   Khi kiểm tra bản gợi ý ban đầu, mình tự bổ sung kiểm tra kiểu `reply`/`reason`/`cited_codes` để tránh lỗi `.strip()` khi `reply` dạng số và chặn trường hợp model trích đúng nguồn `C302-01` nhưng viết sai giờ `23:59` thay vì `17:00`.
   Mình cũng sửa ưu tiên nhận diện chủ đề `B13`, viết lại prompt đánh giá nguồn và kiểm chứng toàn bộ nhánh qua trace tại [traces/run-2.jsonl](../traces/run-2.jsonl). Chi tiết ở [khai báo dùng AI](../docs/ai-usage.md).

3. Một câu thử trượt của nhóm và mình học được gì từ nó:
   `B15` trượt ở Lượt 1 (`22/24`) vì khi thiếu tên bài lab, trợ lý chỉ hỏi lại bài số mấy mà bỏ rơi vướng mắc học viên bị kẹt lúc deploy lên Railway.
   Sau khi mình sửa giữ lại vướng mắc đã che dữ liệu nhạy cảm và hỏi đúng phần còn thiếu mà chưa gọi công cụ tra lịch (`tool_calls=0`), Lượt 2 đạt `24/24` (`100%`) và không có câu nào tệ đi. [Báo cáo đánh giá](../eval/report.md)
   Mình rút ra rằng bước hỏi thêm phải giữ đủ ngữ cảnh người dùng vừa nêu thay vì chỉ gom tham số cho code chạy, và mọi bản sửa đều phải kiểm lại cả chuỗi hội thoại 2 lượt.
