# Khai báo dùng AI

README của nhóm có mục "Dùng AI vào việc gì" (2–3 dòng, bắt buộc). Ghi chi tiết vào bảng dưới đây.

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

Nhóm dùng Codex để rà soát code bản chạy thử và tài liệu, dùng Gamma để dựng bản nháp slide demo.

Thành viên nhóm kiểm tra hành vi của bản chạy thử, đối chiếu output và trace với barem đã chốt, rồi rà số liệu trên slide với báo cáo đánh giá và chi phí.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Code bản chạy thử | Codex | Hỗ trợ rà code và đối chiếu luồng với đặc tả. | Kiểm tra nhánh trả lời, hỏi thêm, gợi ý coach và từ chối qua benchmark và trace. | Trần Dương Trung Tính |
| Prompt / thiết kế lời gọi mô hình | GPT-4o mini qua OpenRouter | Trong bản chạy thử, đánh giá căn cứ đã tra và đề xuất nội dung trả lời hoặc bước xử lý. | Kiểm tra cấu trúc dữ liệu model trả về và đối chiếu câu trả lời với nguồn. | Trần Dương Trung Tính |
| Rà câu hỏi phỏng vấn / khảo sát | Codex | — | Kiểm tra bộ câu hỏi khảo sát và xác nhận 20 phản hồi thuộc mẫu phân tích. | Nguyễn Nhựt Linh |
| Viết câu thử (benchmark) | Codex | Hỗ trợ soạn và rà câu thử. | Kiểm tra `source` và tiêu chí `pass_criterion` cho từng câu. | Nguyễn Nhựt Linh |
| Slide, văn bản | Gamma, Codex | Gamma dựng bản nháp slide. Codex hỗ trợ rà câu chữ và tài liệu. | Đối chiếu số liệu trên slide với báo cáo đánh giá và báo cáo chi phí. | Trần Anh Duy |

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).
