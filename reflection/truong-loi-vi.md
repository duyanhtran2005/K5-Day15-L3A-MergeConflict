# Reflection — Trương Lợi Vĩ

> Làm ở guide bước 5.3. Mỗi người một file: chép file này thành `reflection/<ten-khong-dau>.md` (viết thường, không dấu). Hạn: **23:59 Thứ Bảy 28/11**. Mỗi câu 3–6 dòng.

1. Vai trò + phần mình làm (trỏ tới file / commit):
   Mình phụ trách cấu hình chi phí và kiểm tra khả năng chạy cost simulation cho phần dùng model thật.
   Mình hoàn thiện [cấu hình personas](../cost/personas.yaml) với 50 phiên mô phỏng, 3 persona, các kịch bản low/base/high và hai model OpenRouter để so sánh.
   Mình cũng bàn giao slide cho B01 và B20 tại [deck demo](../slides/demo-b01-b20-run-2.pptx), dựa trên token, số lần gọi tool/model của Run 2.

2. AI hỗ trợ mình thế nào (việc gì, công cụ gì, chỗ nào phải sửa lại output AI):
   Mình dùng Codex để rà code routing, trace token và đối chiếu cấu hình mô phỏng với [Run 2](../eval/run-2.csv) cùng trace tương ứng.
   AI hỗ trợ tìm và đối chiếu giá công bố, nhưng sau khi nhóm xác nhận dùng OpenRouter, mình thay giá/direct model ID trước đó bằng published pricing theo đúng OpenRouter.
   Mình không suy ra tần suất dùng từ dữ liệu khảo sát khi không có trường phù hợp; các giả định quy mô và tần suất được ghi rõ là tự ước tính trong cấu hình.

3. Một câu thử trượt của nhóm và mình học được gì từ nó:
   B20 trượt ở Lượt 1 vì hệ thống hiểu “buổi chiều” trong mô tả tài liệu là ca học của người hỏi, nên đã tra cứu quá sớm.
   Ở Lượt 2, hệ thống hỏi lại ca học trước, không gọi tool hay model; kết quả này được ghi trong [báo cáo đánh giá](../eval/report.md) và trace Run 2.
   Mình học được rằng khi dùng trace để ước tính chi phí, phải tách rõ luồng cần làm rõ ngữ cảnh khỏi luồng gọi model: B20 có 0 token, còn B01 mới có token và chi phí model.
