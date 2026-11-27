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
| Mục đích | Minh họa lịch phân công theo lớp, ngày, ca và phòng. |
| Nguồn | Nhóm dựng thủ công theo [cấu trúc lịch lab của BTC](https://github.com/VinUni-AI20k/K5-L3-Day15-AI-Product-Hackathon/blob/main/data/training-ops/README.md#các-file). |
| Xử lý | Dùng mã coach và Day Lead giả. H209 có hai ca với hai người khác nhau. H210 có một ca thiếu coach. |
| Số dòng và phiên bản | 3 phân công và 1 đầu mối chuyển tiếp, bản CP2 ngày 27/11/2026. |
| Nhãn | Toàn bộ là `synthetic`, viết tay, không dùng seed. |
| Giới hạn | Lịch chỉ dùng cho demo. Mã liên hệ không trỏ đến tài khoản thật. |

Số liệu khảo sát của học viên nằm ở [tổng hợp bằng chứng](../evidence/summary.md) và phục vụ phân tích vấn đề. Hai file JSON là đầu vào cho prototype.

## Dataset 3 · Tin nhắn trong thread lab cho bản mock CP2

| Trường | Nội dung |
| --- | --- |
| File | [lab_thread_messages.csv](lab_thread_messages.csv) |
| Mục đích | Tra đoạn trả lời theo đúng thread, bài, ngày và ca. |
| Nguồn và xử lý | 6 tin nhắn viết tay. Mỗi dòng có mã tin, mã thread, mã bài, ngày, ca, loại nguồn và link minh họa. |
| Nhãn và giới hạn | `synthetic`. Tên phòng lấy từ bối cảnh lab. Nội dung, giờ nộp và link đuôi `.example` là dữ liệu mô phỏng. |

## Dataset 4 · Phân công theo phòng cho bản mock CP2

| Trường | Nội dung |
| --- | --- |
| File | [lab_coach_assignments.csv](lab_coach_assignments.csv) |
| Mục đích | Chỉ gợi ý coach khi lịch xác nhận phòng và phân công theo đúng lớp, ngày và ca. |
| Nguồn và xử lý | 2 dòng viết tay theo cấu trúc lịch giả lập của BTC. Một dòng chưa chốt phòng, một dòng xác nhận coach mẫu. |
| Nhãn và giới hạn | `synthetic`. Tên coach và phân công chỉ dùng chạy thử. |

Bản mock CP2 sử dụng hai file CSV trên. Hai file JSON ở Dataset 1 và 2 ghi các ví dụ minh họa của nhóm.
