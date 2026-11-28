# Reflection — Nguyễn Nhựt Linh

> Làm ở guide bước 5.3. Mỗi người một file: chép file này thành `reflection/<ten-khong-dau>.md` (viết thường, không dấu). Hạn: **23:59 Thứ Bảy 28/11**. Mỗi câu 3–6 dòng.

1. Vai trò + phần mình làm (trỏ tới file / commit):
   Mình phụ trách bằng chứng và dữ liệu, tổng hợp khảo sát về việc cần hỗ trợ gấp ngoài lớp và lưu kết quả ẩn danh. [Tổng hợp khảo sát](../evidence/summary.md)
   Mình mở rộng bộ câu thử từ 12 lên 24 câu, chạy và tổng hợp kết quả hai lượt đánh giá. [Bộ câu thử](../eval/benchmark.csv) · [Báo cáo đánh giá](../eval/report.md)
   Ở CP4, mình chạy mô phỏng chi phí 50 phiên và tổng hợp kết quả. [Báo cáo chi phí](../cost/cost-estimate.md)

2. AI hỗ trợ mình thế nào (việc gì, công cụ gì, chỗ nào phải sửa lại output AI):
   Mình dùng Codex để rà câu chữ trong bộ câu hỏi khảo sát và hỗ trợ soạn, rà các câu thử. [Khai báo dùng AI](../docs/ai-usage.md)
   Mình kiểm tra lại bộ câu hỏi và xác nhận 20 phiếu đủ điều kiện phân tích. Phiếu S21 về xin nghỉ học được giữ trong log và loại khỏi mẫu phân tích. [Hồ sơ khảo sát](../evidence/survey/questions.md)
   Với các câu thử Codex hỗ trợ soạn, mình kiểm tra lại nguồn (`source`) và tiêu chí đạt (`pass_criterion`) của từng câu. [Bộ câu thử](../eval/benchmark.csv)

3. Một câu thử trượt của nhóm và mình học được gì từ nó:
   B15 trượt ở lượt 1 vì trợ lý chỉ hỏi số hoặc tên bài lab, bỏ sót việc học viên đang kẹt khi deploy lên Railway.
   Ở lượt 2, trợ lý ghi nhận vướng mắc deploy Railway rồi hỏi bài lab, nên câu này đạt. [Báo cáo đánh giá](../eval/report.md)
   Mình rút ra rằng khi chấm câu hỏi làm rõ, cần kiểm tra trợ lý có nhắc lại đúng vướng mắc học viên đã nêu và có hỏi đúng dữ kiện còn thiếu hay không.
