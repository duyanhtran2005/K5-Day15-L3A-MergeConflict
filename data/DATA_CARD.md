# Data card — dữ liệu bản chạy thử

## Dataset 1 · Hỏi đáp và thông báo

| Trường | Nội dung |
| --- | --- |
| File | [demo_faq.json](demo_faq.json) |
| Mục đích | Tra câu hỏi về hạn nộp, tên repo, nơi xem hướng dẫn và kênh hỗ trợ. |
| Nguồn | Hai mục diễn giải từ [README của BTC](https://github.com/VinUni-AI20k/K5-L3-Day15-AI-Product-Hackathon/blob/main/README.md#checkpoint). Ba thông báo còn lại do nhóm dựng cho LAB-DEMO-01. |
| Xử lý | Mỗi mục có mã nguồn, chủ đề, buổi áp dụng, nội dung và cờ `synthetic`. Mục chính thức có link. Thông báo giả lập dẫn về mã mục trong file. |
| Số dòng và phiên bản | 5 mục, bản CP2 ngày 27/11/2026. |
| Nhãn | 2 mục nguồn thật, 3 mục `synthetic`. Mục giả lập viết tay, không dùng seed. |
| Giới hạn | Hạn checkpoint áp dụng riêng cho hackathon. Hạn nộp lab, đường dẫn LMS nội bộ và tên kênh trong kịch bản mẫu là giả lập. |

## Dataset 2 · Phân công hỗ trợ lab

| Trường | Nội dung |
| --- | --- |
| File | [demo_lab_schedule.json](demo_lab_schedule.json) |
| Mục đích | Tra người phụ trách theo ngày, ca và phòng, hoặc chuyển Day Lead khi thiếu phân công. |
| Nguồn | Nhóm dựng thủ công theo [cấu trúc lịch lab của BTC](https://github.com/VinUni-AI20k/K5-L3-Day15-AI-Product-Hackathon/blob/main/data/training-ops/README.md#các-file). |
| Xử lý | Dùng mã coach và Day Lead giả. H209 có hai ca với hai người khác nhau. H210 có một ca thiếu coach. |
| Số dòng và phiên bản | 3 phân công và 1 đầu mối chuyển tiếp, bản CP2 ngày 27/11/2026. |
| Nhãn | Toàn bộ là `synthetic`, viết tay, không dùng seed. |
| Giới hạn | Lịch chỉ dùng cho demo. Mã liên hệ không trỏ đến tài khoản thật. |

Số liệu khảo sát của học viên nằm ở [tổng hợp bằng chứng](../evidence/summary.md) và phục vụ phân tích vấn đề. Hai file JSON là đầu vào cho prototype.
